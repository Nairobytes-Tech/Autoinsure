"use client";

import { useNotifications } from "@/hooks/use-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Bell } from "lucide-react";
import { formatDateTime } from "@/lib/utils";
import { useState } from "react";
import { Pagination } from "@/components/ui/pagination";

export default function NotificationsPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useNotifications({ page, page_size: 20 });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Notifications</h2>
        <p className="text-muted-foreground">View your notifications</p>
      </div>
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Type</TableHead>
                <TableHead>Subject</TableHead>
                <TableHead>Message</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Read</TableHead>
                <TableHead>Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array.from({ length: 10 }).map((_, i) => (
                  <TableRow key={i}><TableCell colSpan={6} className="text-center">Loading...</TableCell></TableRow>
                ))
              ) : data?.results?.map((n) => (
                <TableRow key={n.id} className={!n.is_read ? "bg-primary/5" : ""}>
                  <TableCell className="capitalize">{n.notification_type?.replace(/_/g, " ")}</TableCell>
                  <TableCell className="font-medium">{n.subject || "-"}</TableCell>
                  <TableCell className="max-w-md truncate">{n.message}</TableCell>
                  <TableCell>
                    <Badge variant={n.priority === "urgent" ? "destructive" : n.priority === "high" ? "warning" : "secondary"}>
                      {n.priority}
                    </Badge>
                  </TableCell>
                  <TableCell>{n.is_read ? "Yes" : "No"}</TableCell>
                  <TableCell>{formatDateTime(n.created_at)}</TableCell>
                </TableRow>
              ))}
              {data?.results?.length === 0 && (
                <TableRow><TableCell colSpan={6} className="py-8 text-center text-muted-foreground"><Bell className="mx-auto mb-2 h-8 w-8 opacity-50" />No notifications</TableCell></TableRow>
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
