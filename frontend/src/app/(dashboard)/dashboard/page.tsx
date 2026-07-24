"use client";

import { StatCard, StatCardSkeleton } from "@/components/ui/stat-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { StatusBadge } from "@/components/ui/status-badge";
import { usePolicies, useClaims, useCustomers, usePayments } from "@/hooks/use-api";
import { FileText, Shield, Users, Receipt, TrendingUp, AlertTriangle } from "lucide-react";
import { formatCurrency, formatDate } from "@/lib/utils";

export default function DashboardPage() {
  const { data: policies, isLoading: pLoading } = usePolicies({ page_size: 5 });
  const { data: claims, isLoading: cLoading } = useClaims({ page_size: 5 });
  const { data: customers, isLoading: cuLoading } = useCustomers({ page_size: 1 });
  const { data: payments, isLoading: paLoading } = usePayments({ page_size: 5 });

  const totalPolicies = policies?.pagination?.count || 0;
  const totalClaims = claims?.pagination?.count || 0;
  const totalCustomers = customers?.pagination?.count || 0;
  const totalRevenue = payments?.results?.reduce((sum, p) => sum + (p.payment_status === "completed" ? p.amount : 0), 0) || 0;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">Welcome back. Here&apos;s an overview of your operations.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {pLoading || cuLoading || paLoading ? (
          Array.from({ length: 4 }).map((_, i) => <StatCardSkeleton key={i} />)
        ) : (
          <>
            <StatCard title="Total Policies" value={totalPolicies} icon={<FileText className="h-4 w-4" />} description="All time policies" />
            <StatCard title="Active Claims" value={totalClaims} icon={<Shield className="h-4 w-4" />} description="Claims in progress" />
            <StatCard title="Total Customers" value={totalCustomers} icon={<Users className="h-4 w-4" />} description="Registered customers" />
            <StatCard title="Revenue" value={formatCurrency(totalRevenue)} icon={<Receipt className="h-4 w-4" />} description="Collected payments" />
          </>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" /> Recent Policies
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Policy #</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Premium</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pLoading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <TableRow key={i}><TableCell colSpan={3}>Loading...</TableCell></TableRow>
                  ))
                ) : policies?.results?.map((p) => (
                  <TableRow key={p.id}>
                    <TableCell className="font-medium">{p.policy_number}</TableCell>
                    <TableCell><StatusBadge status={p.policy_status} /></TableCell>
                    <TableCell>{formatCurrency(p.premium_amount)}</TableCell>
                  </TableRow>
                ))}
                {policies?.results?.length === 0 && (
                  <TableRow><TableCell colSpan={3} className="text-center text-muted-foreground">No policies yet</TableCell></TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" /> Recent Claims
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Claim #</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Amount</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {cLoading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <TableRow key={i}><TableCell colSpan={3}>Loading...</TableCell></TableRow>
                  ))
                ) : claims?.results?.map((c) => (
                  <TableRow key={c.id}>
                    <TableCell className="font-medium">{c.claim_number}</TableCell>
                    <TableCell><StatusBadge status={c.claim_status} /></TableCell>
                    <TableCell>{formatCurrency(c.claim_amount)}</TableCell>
                  </TableRow>
                ))}
                {claims?.results?.length === 0 && (
                  <TableRow><TableCell colSpan={3} className="text-center text-muted-foreground">No claims yet</TableCell></TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Receipt className="h-4 w-4" /> Recent Payments
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Reference</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Amount</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {paLoading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <TableRow key={i}><TableCell colSpan={3}>Loading...</TableCell></TableRow>
                  ))
                ) : payments?.results?.map((p) => (
                  <TableRow key={p.id}>
                    <TableCell className="font-medium">{p.reference_number}</TableCell>
                    <TableCell><StatusBadge status={p.payment_status} /></TableCell>
                    <TableCell>{formatCurrency(p.amount)}</TableCell>
                  </TableRow>
                ))}
                {payments?.results?.length === 0 && (
                  <TableRow><TableCell colSpan={3} className="text-center text-muted-foreground">No payments yet</TableCell></TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-4 w-4" /> Claims by Type
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {["accident", "theft", "fire", "natural_disaster", "vandalism", "other"].map((type) => {
                const count = claims?.results?.filter((c) => c.claim_type === type).length || 0;
                return (
                  <div key={type} className="flex items-center justify-between">
                    <span className="text-sm capitalize">{type.replace(/_/g, " ")}</span>
                    <span className="text-sm font-medium">{count}</span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
