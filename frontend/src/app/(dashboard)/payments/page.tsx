"use client";

import { usePayments } from "@/hooks/use-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { StatusBadge } from "@/components/ui/status-badge";
import { DataTableToolbar } from "@/components/ui/data-table-toolbar";
import { Pagination } from "@/components/ui/pagination";
import { Card, CardContent } from "@/components/ui/card";
import { formatCurrency, formatDate } from "@/lib/utils";
import { useState } from "react";

export default function PaymentsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const { data, isLoading } = usePayments({ page, search: search || undefined, page_size: 20 });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Payments</h2>
        <p className="text-muted-foreground">Manage payments and receipts</p>
      </div>
      <Card>
        <CardContent className="p-0">
          <DataTableToolbar searchPlaceholder="Search by reference..." searchValue={search} onSearchChange={(v) => { setSearch(v); setPage(1); }} />
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Reference</TableHead>
                <TableHead>For</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Payer</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Paid</TableHead>
                <TableHead>Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <TableRow key={i}><TableCell colSpan={7} className="text-center">Loading...</TableCell></TableRow>
                ))
              ) : data?.results?.map((p) => (
                <TableRow key={p.id}>
                  <TableCell className="font-medium">{p.reference_number}</TableCell>
                  <TableCell className="capitalize">{p.payment_for?.replace(/_/g, " ")}</TableCell>
                  <TableCell><StatusBadge status={p.payment_status} /></TableCell>
                  <TableCell>{p.payer_name || "-"}</TableCell>
                  <TableCell>{formatCurrency(p.amount)}</TableCell>
                  <TableCell>{formatCurrency(p.paid_amount)}</TableCell>
                  <TableCell>{formatDate(p.payment_date)}</TableCell>
                </TableRow>
              ))}
              {data?.results?.length === 0 && (
                <TableRow><TableCell colSpan={7} className="py-8 text-center text-muted-foreground">No payments found</TableCell></TableRow>
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
