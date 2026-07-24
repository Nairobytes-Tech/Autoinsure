"use client";

import { useBranches } from "@/hooks/use-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { StatusBadge } from "@/components/ui/status-badge";
import { DataTableToolbar } from "@/components/ui/data-table-toolbar";
import { Pagination } from "@/components/ui/pagination";
import { Card, CardContent } from "@/components/ui/card";
import { formatCurrency } from "@/lib/utils";
import { useState } from "react";

export default function BranchesPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const { data, isLoading } = useBranches({ page, search: search || undefined, page_size: 20 });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Branches</h2>
        <p className="text-muted-foreground">Manage branch offices</p>
      </div>
      <Card>
        <CardContent className="p-0">
          <DataTableToolbar searchPlaceholder="Search branches..." searchValue={search} onSearchChange={(v) => { setSearch(v); setPage(1); }} />
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Code</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>City</TableHead>
                <TableHead>State</TableHead>
                <TableHead>Policies</TableHead>
                <TableHead>Customers</TableHead>
                <TableHead>Premium Target</TableHead>
                <TableHead>Achieved</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <TableRow key={i}><TableCell colSpan={10} className="text-center">Loading...</TableCell></TableRow>
                ))
              ) : data?.results?.map((b) => (
                <TableRow key={b.id}>
                  <TableCell className="font-medium">{b.code}</TableCell>
                  <TableCell>{b.name}</TableCell>
                  <TableCell className="capitalize">{b.branch_type?.replace(/_/g, " ")}</TableCell>
                  <TableCell>{b.city || "-"}</TableCell>
                  <TableCell>{b.state || "-"}</TableCell>
                  <TableCell>{b.total_policies}</TableCell>
                  <TableCell>{b.total_customers}</TableCell>
                  <TableCell>{formatCurrency(b.target_premium)}</TableCell>
                  <TableCell>{formatCurrency(b.achieved_premium)}</TableCell>
                  <TableCell><StatusBadge status={b.status} /></TableCell>
                </TableRow>
              ))}
              {data?.results?.length === 0 && (
                <TableRow><TableCell colSpan={10} className="py-8 text-center text-muted-foreground">No branches found</TableCell></TableRow>
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
