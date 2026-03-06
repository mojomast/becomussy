"use client";

interface Column<T> {
  key: string;
  label: string;
  render?: (row: T) => React.ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  rows: T[];
  onRowClick?: (row: T) => void;
  loading?: boolean;
  emptyMessage?: string;
  // Pagination
  total?: number;
  limit?: number;
  offset?: number;
  onPageChange?: (offset: number) => void;
}

export function DataTable<T extends Record<string, unknown>>({
  columns,
  rows,
  onRowClick,
  loading,
  emptyMessage = "No data found",
  total,
  limit = 20,
  offset = 0,
  onPageChange,
}: DataTableProps<T>) {
  const totalPages = total != null ? Math.ceil(total / limit) : undefined;
  const currentPage = Math.floor(offset / limit) + 1;

  if (loading) {
    return (
      <div className="py-12 text-center" style={{ color: "var(--text-secondary)" }}>
        Loading...
      </div>
    );
  }

  if (rows.length === 0) {
    return (
      <div className="py-12 text-center" style={{ color: "var(--text-secondary)" }}>
        {emptyMessage}
      </div>
    );
  }

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border)" }}>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={`text-left py-2 px-3 text-xs font-medium uppercase tracking-wider ${col.className || ""}`}
                  style={{ color: "var(--text-secondary)" }}
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr
                key={(row.id as string) || i}
                onClick={() => onRowClick?.(row)}
                className={onRowClick ? "cursor-pointer" : ""}
                style={{
                  borderBottom: "1px solid var(--border)",
                }}
                onMouseEnter={(e) => {
                  if (onRowClick) (e.currentTarget.style.backgroundColor = "var(--bg-hover)");
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget.style.backgroundColor = "transparent");
                }}
              >
                {columns.map((col) => (
                  <td key={col.key} className={`py-2.5 px-3 ${col.className || ""}`}>
                    {col.render
                      ? col.render(row)
                      : String(row[col.key] ?? "—")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages != null && totalPages > 1 && onPageChange && (
        <div className="flex items-center justify-between mt-4 pt-3" style={{ borderTop: "1px solid var(--border)" }}>
          <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
            Page {currentPage} of {totalPages} ({total} total)
          </span>
          <div className="flex gap-2">
            <button
              disabled={offset === 0}
              onClick={() => onPageChange(Math.max(0, offset - limit))}
              className="px-3 py-1 rounded text-xs border disabled:opacity-30"
              style={{
                borderColor: "var(--border)",
                color: "var(--text-secondary)",
              }}
            >
              Previous
            </button>
            <button
              disabled={currentPage >= totalPages}
              onClick={() => onPageChange(offset + limit)}
              className="px-3 py-1 rounded text-xs border disabled:opacity-30"
              style={{
                borderColor: "var(--border)",
                color: "var(--text-secondary)",
              }}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
