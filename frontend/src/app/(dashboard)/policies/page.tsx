"use client";

import { usePolicies } from "@/hooks/use-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { StatusBadge } from "@/components/ui/status-badge";
import { DataTableToolbar } from "@/components/ui/data-table-toolbar";
import { Pagination } from "@/components/ui/pagination";
import { Card, CardContent } from "@/components/ui/card";
import { formatCurrency, formatDate } from "@/lib/utils";
import Link from "next/link";
import { useState } from "react";

export default function PoliciesPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const { data, isLoading } = usePolicies({ page, search: search || undefined, page_size: 20 });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Policies</h2>
        <p className="text-muted-foreground">Manage insurance policies</p>
      </div>
      <Card>
        <CardContent className="p-0">
          <DataTableToolbar searchPlaceholder="Search by policy number..." searchValue={search} onSearchChange={(v) => { setSearch(v); setPage(1); }} />
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Policy #</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Payment</TableHead>
                <TableHead>Start Date</TableHead>
                <TableHead>End Date</TableHead>
                <TableHead>Premium</TableHead>
                <TableHead>Sum Insured</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <TableRow key={i}><TableCell colSpan={8} className="text-center">Loading...</TableCell></TableRow>
                ))
              ) : data?.results?.map((p) => (
                <TableRow key={p.id}>
                  <TableCell><Link href={`/policies/${p.id}`} className="font-medium text-primary hover:underline">{p.policy_number}</Link></TableCell>
                  <TableCell className="capitalize">{p.policy_type?.replace(/_/g, " ")}</TableCell>
                  <TableCell><StatusBadge status={p.policy_status} /></TableCell>
                  <TableCell><StatusBadge status={p.payment_status} /></TableCell>
                  <TableCell>{formatDate(p.start_date)}</TableCell>
                  <TableCell>{formatDate(p.end_date)}</TableCell>
                  <TableCell>{formatCurrency(p.premium_amount)}</TableCell>
                  <TableCell>{formatCurrency(p.sum_insured)}</TableCell>
                </TableRow>
              ))}
              {data?.results?.length === 0 && (
                <TableRow><TableCell colSpan={8} className="py-8 text-center text-muted-foreground">No policies found</TableCell></TableRow>
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
