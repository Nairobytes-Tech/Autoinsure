"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard, Users, FileText, Shield, Receipt, Package, UserCheck,
  Building2, Truck, Bell, BarChart3, Settings, ClipboardList, FileSearch,
  Scale, Brain, GitBranch, ScrollText, ChevronLeft, ChevronRight,
} from "lucide-react";
import { useState } from "react";

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Customers", href: "/customers", icon: Users },
  { label: "Policies", href: "/policies", icon: FileText },
  { label: "Claims", href: "/claims", icon: Shield },
  { label: "Quotes", href: "/quotes", icon: ClipboardList },
  { label: "Payments", href: "/payments", icon: Receipt },
  { label: "Products", href: "/products", icon: Package },
  { label: "Agents", href: "/agents", icon: UserCheck },
  { label: "Brokers", href: "/brokers", icon: Building2 },
  { label: "Dealers", href: "/dealers", icon: Truck },
  { label: "Branches", href: "/branches", icon: Building2 },
  { label: "Underwriting", href: "/underwriting", icon: Scale },
  { label: "Reports", href: "/reports", icon: BarChart3 },
  { label: "Notifications", href: "/notifications", icon: Bell },
  { label: "Audit Logs", href: "/audit", icon: FileSearch },
  { label: "Workflows", href: "/workflows", icon: GitBranch },
  { label: "AI Features", href: "/ai", icon: Brain },
  { label: "Documents", href: "/documents", icon: ScrollText },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className={cn(
      "flex flex-col border-r bg-card transition-all duration-300",
      collapsed ? "w-16" : "w-64"
    )}>
      <div className="flex h-14 items-center border-b px-4">
        {!collapsed && <span className="text-lg font-bold text-primary">AutoInsure</span>}
        <button onClick={() => setCollapsed(!collapsed)} className="ml-auto rounded p-1 hover:bg-muted">
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>
      <nav className="flex-1 overflow-y-auto py-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 mx-2 text-sm font-medium transition-colors",
                isActive ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-muted hover:text-foreground",
                collapsed && "justify-center px-2"
              )}
              title={collapsed ? item.label : undefined}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
