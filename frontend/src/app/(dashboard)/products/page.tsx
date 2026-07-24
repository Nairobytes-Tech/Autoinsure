"use client";

import { useProducts } from "@/hooks/use-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { StatusBadge } from "@/components/ui/status-badge";
import { DataTableToolbar } from "@/components/ui/data-table-toolbar";
import { Pagination } from "@/components/ui/pagination";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/lib/utils";
import { useState } from "react";

export default function ProductsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const { data, isLoading } = useProducts({ page, search: search || undefined, page_size: 20 });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Products</h2>
        <p className="text-muted-foreground">Manage insurance products</p>
      </div>
      <Card>
        <CardContent className="p-0">
          <DataTableToolbar searchPlaceholder="Search products..." searchValue={search} onSearchChange={(v) => { setSearch(v); setPage(1); }} />
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Code</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Billing</TableHead>
                <TableHead>Base Premium</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Featured</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <TableRow key={i}><TableCell colSpan={7} className="text-center">Loading...</TableCell></TableRow>
                ))
              ) : data?.results?.map((p) => (
                <TableRow key={p.id}>
                  <TableCell className="font-medium">{p.name}</TableCell>
                  <TableCell>{p.code}</TableCell>
                  <TableCell className="capitalize">{p.product_type?.replace(/_/g, " ")}</TableCell>
                  <TableCell className="capitalize">{p.billing_frequency?.replace(/_/g, " ")}</TableCell>
                  <TableCell>{formatCurrency(p.base_premium)}</TableCell>
                  <TableCell><StatusBadge status={p.status} /></TableCell>
                  <TableCell>{p.is_featured ? <Badge>Featured</Badge> : "-"}</TableCell>
                </TableRow>
              ))}
              {data?.results?.length === 0 && (
                <TableRow><TableCell colSpan={7} className="py-8 text-center text-muted-foreground">No products found</TableCell></TableRow>
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
