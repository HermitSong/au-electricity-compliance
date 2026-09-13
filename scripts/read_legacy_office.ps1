param(
    [Parameter(Mandatory=$true)][string]$Source,
    [Parameter(Mandatory=$true)][ValidateSet('rtf','doc')][string]$Format
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$units = [System.Collections.Generic.List[object]]::new()
if ($Format -eq 'rtf') {
    Add-Type -AssemblyName PresentationFramework
    $document = [System.Windows.Documents.FlowDocument]::new()
    $range = [System.Windows.Documents.TextRange]::new($document.ContentStart, $document.ContentEnd)
    $stream = [System.IO.File]::OpenRead($Source)
    try { $range.Load($stream, [System.Windows.DataFormats]::Rtf) } finally { $stream.Dispose() }
    function Read-Blocks($blocks, [string]$prefix) {
        $number = 0
        foreach ($block in $blocks) {
            $number++
            $locator = "${prefix}:block:$number"
            if ($block -is [System.Windows.Documents.Table]) {
                $groupNumber = 0
                foreach ($group in $block.RowGroups) {
                    $groupNumber++
                    $rowNumber = 0
                    foreach ($row in $group.Rows) {
                        $rowNumber++
                        $cellNumber = 0
                        foreach ($cell in $row.Cells) {
                            $cellNumber++
                            $cellLocator = "${locator}:table:group:${groupNumber}:row:${rowNumber}:cell:$cellNumber"
                            $text = [System.Windows.Documents.TextRange]::new($cell.ContentStart, $cell.ContentEnd).Text.Trim()
                            if ($text) { $units.Add(@{locator=$cellLocator; text=$text; row_span=$cell.RowSpan; column_span=$cell.ColumnSpan}) }
                        }
                    }
                }
            } elseif ($block -is [System.Windows.Documents.List]) {
                $itemNumber = 0
                foreach ($item in $block.ListItems) {
                    $itemNumber++
                    Read-Blocks $item.Blocks "${locator}:list-item:$itemNumber"
                }
            } elseif ($block -is [System.Windows.Documents.Section]) {
                Read-Blocks $block.Blocks "${locator}:section"
            } else {
                $text = [System.Windows.Documents.TextRange]::new($block.ContentStart, $block.ContentEnd).Text.Trim()
                if ($text) { $units.Add(@{locator=$locator; text=$text}) }
            }
        }
    }
    Read-Blocks $document.Blocks 'rtf:body'
    $parser = [System.Windows.Documents.FlowDocument].Assembly.FullName
} else {
    # Windows' registered legacy Office filter is an in-process, read-only parser.
    Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
namespace OfficeRecovery {
    [StructLayout(LayoutKind.Sequential)] public struct PropSpec { public uint kind; public IntPtr value; }
    [StructLayout(LayoutKind.Sequential)] public struct FullPropSpec { public Guid guid; public PropSpec prop; }
    [StructLayout(LayoutKind.Sequential)] public struct Chunk {
        public uint id, breakType, flags, locale;
        public FullPropSpec property;
        public uint sourceId, start, length;
    }
    [ComImport, Guid("89BCB740-6119-101A-BCB7-00DD010655AF"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IFilter {
        [PreserveSig] int Init(uint flags, uint count, IntPtr attributes, out uint resultFlags);
        [PreserveSig] int GetChunk(out Chunk chunk);
        [PreserveSig] int GetText(ref uint count, [Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder text);
        [PreserveSig] int GetValue(ref IntPtr value);
        [PreserveSig] int BindRegion(IntPtr region, ref Guid iid, ref IntPtr value);
    }
    public class TextChunk { public uint id, break_type, source_id, source_start, source_length; public string text; }
    public static class Reader {
        [DllImport("query.dll", CharSet=CharSet.Unicode)]
        static extern int LoadIFilter(string path, IntPtr outer, out IFilter filter);
        public static List<TextChunk> Read(string path) {
            IFilter filter;
            Marshal.ThrowExceptionForHR(LoadIFilter(path, IntPtr.Zero, out filter));
            try {
                uint flags;
                Marshal.ThrowExceptionForHR(filter.Init(0, 0, IntPtr.Zero, out flags));
                var result = new List<TextChunk>();
                for (int n=0; n<100000; n++) {
                    Chunk chunk;
                    int hr = filter.GetChunk(out chunk);
                    if (hr == unchecked((int)0x80041700)) return result;
                    Marshal.ThrowExceptionForHR(hr);
                    if ((chunk.flags & 1) == 0) continue;
                    var all = new StringBuilder();
                    for (int k=0; k<100000; k++) {
                        uint count = 4096;
                        var buffer = new StringBuilder(4096);
                        hr = filter.GetText(ref count, buffer);
                        if (hr == unchecked((int)0x80041701)) break;
                        Marshal.ThrowExceptionForHR(hr);
                        all.Append(buffer.ToString(0, (int)count));
                        if (all.Length > 20000000) throw new Exception("DOC text limit exceeded");
                        if (hr == 0x41709) break;
                        if (k == 99999) throw new Exception("DOC chunk text limit exceeded");
                    }
                    if (!String.IsNullOrWhiteSpace(all.ToString())) result.Add(new TextChunk {
                        id=chunk.id, break_type=chunk.breakType, source_id=chunk.sourceId,
                        source_start=chunk.start, source_length=chunk.length, text=all.ToString().Trim()
                    });
                }
                throw new Exception("DOC chunk limit exceeded");
            } finally { Marshal.FinalReleaseComObject(filter); }
        }
    }
}
'@
    foreach ($chunk in [OfficeRecovery.Reader]::Read($Source)) {
        $units.Add(@{locator="doc:ifilter:chunk:$($chunk.id)"; text=$chunk.text; break_type=$chunk.break_type;
            source_chunk=$chunk.source_id; source_start=$chunk.source_start; source_length=$chunk.source_length})
    }
    $filterPath = Join-Path ([Environment]::SystemDirectory) 'offfilt.dll'
    $parser = 'Windows IFilter; offfilt.dll ' + [System.Diagnostics.FileVersionInfo]::GetVersionInfo($filterPath).FileVersion
}
@{parser=$parser; units=@($units.ToArray())} | ConvertTo-Json -Depth 12 -Compress
