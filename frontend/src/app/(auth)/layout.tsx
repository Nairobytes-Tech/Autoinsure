"use client";

import { useAuth } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) router.push("/dashboard");
  }, [isAuthenticated, isLoading, router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/50">
      {children}
    </div>
  );
}
