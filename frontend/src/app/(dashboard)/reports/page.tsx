"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart3, FileText, Shield, Users } from "lucide-react";

export default function ReportsPage() {
  const reportTypes = [
    { title: "Premium Collection", description: "Track premium collections by period", icon: <BarChart3 className="h-5 w-5" /> },
    { title: "Claims Summary", description: "Overview of claims by type and status", icon: <Shield className="h-5 w-5" /> },
    { title: "Policy Register", description: "Complete list of all policies", icon: <FileText className="h-5 w-5" /> },
    { title: "Agent Performance", description: "Agent sales and commission metrics", icon: <Users className="h-5 w-5" /> },
    { title: "Revenue Report", description: "Revenue breakdown and trends", icon: <BarChart3 className="h-5 w-5" /> },
    { title: "Commission Report", description: "Commission calculations and payments", icon: <FileText className="h-5 w-5" /> },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Reports</h2>
        <p className="text-muted-foreground">Generate and view business reports</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {reportTypes.map((report) => (
          <Card key={report.title} className="cursor-pointer transition-shadow hover:shadow-md">
            <CardHeader className="flex flex-row items-center gap-3">
              <div className="rounded-md bg-primary/10 p-2 text-primary">{report.icon}</div>
              <CardTitle className="text-base">{report.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{report.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
