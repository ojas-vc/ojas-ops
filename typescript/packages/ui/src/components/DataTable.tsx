"use client";

import type { ReactNode } from "react";

export interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => ReactNode;
  width?: string;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyField?: keyof T;
  isLoading?: boolean;
  emptyMessage?: string;
  onRowClick?: (item: T) => void;
  pagination?: {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
  };
}

export function DataTable<T extends object>({
  columns,
  data,
  keyField = "id" as keyof T,
  isLoading = false,
  emptyMessage = "No records found.",
  onRowClick,
  pagination,
}: DataTableProps<T>) {
  return (
    <div className="w-full space-y-3">
      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/40 shadow-sm">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="border-b border-slate-800 bg-slate-900/80 uppercase tracking-wider text-slate-400 font-semibold">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  style={col.width ? { width: col.width } : undefined}
                  className="px-4 py-3"
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-800/60 font-sans">
            {isLoading ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-8 text-center text-slate-400">
                  <span className="inline-block animate-pulse">Loading data from backend...</span>
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-8 text-center text-slate-500">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((item, idx) => {
                const rowKey = String(item[keyField] ?? idx);
                return (
                  <tr
                    key={rowKey}
                    onClick={() => onRowClick?.(item)}
                    className={`transition-colors ${
                      onRowClick ? "cursor-pointer hover:bg-slate-800/40" : "hover:bg-slate-800/20"
                    }`}
                  >
                    {columns.map((col) => (
                      <td key={`${rowKey}-${col.key}`} className="px-4 py-3">
                        {col.render
                          ? col.render(item)
                          : String((item as Record<string, unknown>)[col.key] ?? "-")}
                      </td>
                    ))}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {pagination && pagination.totalPages > 1 && (
        <div className="flex items-center justify-between px-2 text-xs text-slate-400">
          <span>
            Page {pagination.currentPage} of {pagination.totalPages}
          </span>
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              disabled={pagination.currentPage <= 1}
              onClick={() => pagination.onPageChange(pagination.currentPage - 1)}
              className="rounded-md border border-slate-800 bg-slate-900 px-2.5 py-1 text-xs text-slate-300 hover:bg-slate-800 disabled:opacity-40 transition"
            >
              Previous
            </button>
            <button
              type="button"
              disabled={pagination.currentPage >= pagination.totalPages}
              onClick={() => pagination.onPageChange(pagination.currentPage + 1)}
              className="rounded-md border border-slate-800 bg-slate-900 px-2.5 py-1 text-xs text-slate-300 hover:bg-slate-800 disabled:opacity-40 transition"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
