"use client";

import { useClaims } from "@/hooks/use-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { StatusBadge } from "@/components/ui/status-badge";
import { DataTableToolbar } from "@/components/ui/data-table-toolbar";
import { Pagination } from "@/components/ui/pagination";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatCurrency, formatDate } from "@/lib/utils";
import Link from "next/link";
import { useState } from "react";

export default function ClaimsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const { data, isLoading } = useClaims({ page, search: search || undefined, page_size: 20 });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Claims</h2>
        <p className="text-muted-foreground">Manage insurance claims</p>
      </div>
      <Card>
        <CardContent className="p-0">
          <DataTableToolbar searchPlaceholder="Search by claim number..." searchValue={search} onSearchChange={(v) => { setSearch(v); setPage(1); }} />
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Claim #</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Incident Date</TableHead>
                <TableHead>Claim Amount</TableHead>
                <TableHead>Approved</TableHead>
                <TableHead>Paid</TableHead>
                <TableHead>Fraud</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <TableRow key={i}><TableCell colSpan={9} className="text-center">Loading...</TableCell></TableRow>
                ))
              ) : data?.results?.map((c) => (
                <TableRow key={c.id}>
                  <TableCell><Link href={`/claims/${c.id}`} className="font-medium text-primary hover:underline">{c.claim_number}</Link></TableCell>
                  <TableCell className="capitalize">{c.claim_type?.replace(/_/g, " ")}</TableCell>
                  <TableCell><StatusBadge status={c.claim_status} /></TableCell>
                  <TableCell><Badge variant={c.priority === "high" || c.priority === "urgent" ? "destructive" : "secondary"}>{c.priority}</Badge></TableCell>
                  <TableCell>{formatDate(c.incident_date)}</TableCell>
                  <TableCell>{formatCurrency(c.claim_amount)}</TableCell>
                  <TableCell>{formatCurrency(c.approved_amount)}</TableCell>
                  <TableCell>{formatCurrency(c.paid_amount)}</TableCell>
                  <TableCell>{c.fraud_flag ? <Badge variant="destructive">Flagged</Badge> : "-"}</TableCell>
                </TableRow>
              ))}
              {data?.results?.length === 0 && (
                <TableRow><TableCell colSpan={9} className="py-8 text-center text-muted-foreground">No claims found</TableCell></TableRow>
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
