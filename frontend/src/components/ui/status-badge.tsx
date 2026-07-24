"use client";

import { Badge } from "@/components/ui/badge";

const statusConfig: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "success" | "warning" | "outline" }> = {
  active: { label: "Active", variant: "success" },
  inactive: { label: "Inactive", variant: "secondary" },
  pending: { label: "Pending", variant: "warning" },
  suspended: { label: "Suspended", variant: "destructive" },
  draft: { label: "Draft", variant: "outline" },
  approved: { label: "Approved", variant: "success" },
  rejected: { label: "Rejected", variant: "destructive" },
  expired: { label: "Expired", variant: "secondary" },
  cancelled: { label: "Cancelled", variant: "destructive" },
  paid: { label: "Paid", variant: "success" },
  unpaid: { label: "Unpaid", variant: "destructive" },
  completed: { label: "Completed", variant: "success" },
  new: { label: "New", variant: "default" },
  closed: { label: "Closed", variant: "secondary" },
  under_investigation: { label: "Under Investigation", variant: "warning" },
  assessed: { label: "Assessed", variant: "default" },
  partially_paid: { label: "Partial", variant: "warning" },
  converted: { label: "Converted", variant: "success" },
  quoted: { label: "Quoted", variant: "default" },
  accepted: { label: "Accepted", variant: "success" },
  declined: { label: "Declined", variant: "destructive" },
  processing: { label: "Processing", variant: "warning" },
  failed: { label: "Failed", variant: "destructive" },
  refunded: { label: "Refunded", variant: "secondary" },
  overdue: { label: "Overdue", variant: "destructive" },
  confirmed: { label: "Confirmed", variant: "success" },
  calculated: { label: "Calculated", variant: "default" },
  sent: { label: "Sent", variant: "default" },
};

export function StatusBadge({ status }: { status: string }) {
  const config = statusConfig[status] || { label: status, variant: "outline" as const };
  return <Badge variant={config.variant}>{config.label}</Badge>;
}
