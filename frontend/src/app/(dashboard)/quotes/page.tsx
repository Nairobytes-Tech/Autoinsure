"use client";

import { useQuotes } from "@/hooks/use-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { StatusBadge } from "@/components/ui/status-badge";
import { DataTableToolbar } from "@/components/ui/data-table-toolbar";
import { Pagination } from "@/components/ui/pagination";
import { Card, CardContent } from "@/components/ui/card";
import { formatCurrency, formatDate } from "@/lib/utils";
import Link from "next/link";
import { useState } from "react";

export default function QuotesPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const { data, isLoading } = useQuotes({ page, search: search || undefined, page_size: 20 });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Quotes</h2>
        <p className="text-muted-foreground">Manage insurance quotes</p>
      </div>
      <Card>
        <CardContent className="p-0">
          <DataTableToolbar searchPlaceholder="Search by quote number..." searchValue={search} onSearchChange={(v) => { setSearch(v); setPage(1); }} />
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Quote #</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>Valid Until</TableHead>
                <TableHead>Premium</TableHead>
                <TableHead>Sum Insured</TableHead>
                <TableHead>Net Premium</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <TableRow key={i}><TableCell colSpan={7} className="text-center">Loading...</TableCell></TableRow>
                ))
              ) : data?.results?.map((q) => (
                <TableRow key={q.id}>
                  <TableCell><span className="font-medium text-primary">{q.quote_number}</span></TableCell>
                  <TableCell><StatusBadge status={q.quote_status} /></TableCell>
                  <TableCell className="capitalize">{q.source}</TableCell>
                  <TableCell>{formatDate(q.valid_until)}</TableCell>
                  <TableCell>{formatCurrency(q.premium_amount)}</TableCell>
                  <TableCell>{formatCurrency(q.sum_insured)}</TableCell>
                  <TableCell>{formatCurrency(q.net_premium)}</TableCell>
                </TableRow>
              ))}
              {data?.results?.length === 0 && (
                <TableRow><TableCell colSpan={7} className="py-8 text-center text-muted-foreground">No quotes found</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
          {data?.pagination && (
            <Pagination currentPage={data.pagination.current_page} totalPages={data.pagination.total_pages} onPageChange={setPage} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
