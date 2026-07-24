"use client";

import { useState } from "react";
import { useCustomers } from "@/hooks/use-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { StatusBadge } from "@/components/ui/status-badge";
import { DataTableToolbar } from "@/components/ui/data-table-toolbar";
import { Pagination } from "@/components/ui/pagination";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency, formatDate } from "@/lib/utils";
import Link from "next/link";

export default function CustomersPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const { data, isLoading } = useCustomers({ page, search: search || undefined, page_size: 20 });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Customers</h2>
        <p className="text-muted-foreground">Manage your customer database</p>
      </div>

      <Card>
        <CardContent className="p-0">
          <DataTableToolbar searchPlaceholder="Search customers..." searchValue={search} onSearchChange={(v) => { setSearch(v); setPage(1); }} />
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Phone</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Policies</TableHead>
                <TableHead>Premium Paid</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <TableRow key={i}><TableCell colSpan={7} className="text-center">Loading...</TableCell></TableRow>
                ))
              ) : data?.results?.map((c) => (
                <TableRow key={c.id}>
                  <TableCell>
                    <Link href={`/customers/${c.id}`} className="font-medium text-primary hover:underline">{c.full_name}</Link>
                  </TableCell>
                  <TableCell>{c.email}</TableCell>
                  <TableCell>{c.phone}</TableCell>
                  <TableCell className="capitalize">{c.source || "-"}</TableCell>
                  <TableCell><StatusBadge status={c.status} /></TableCell>
                  <TableCell>{c.active_policies_count}</TableCell>
                  <TableCell>{formatCurrency(c.total_premium_paid)}</TableCell>
                </TableRow>
              ))}
              {data?.results?.length === 0 && (
                <TableRow><TableCell colSpan={7} className="py-8 text-center text-muted-foreground">No customers found</TableCell></TableRow>
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
