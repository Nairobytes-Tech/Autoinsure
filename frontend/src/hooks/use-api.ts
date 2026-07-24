"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import type { PaginatedResponse, Customer, Policy, Claim, Quote, Payment, Product, Agent, Broker, Dealer, Branch, AuditLog, Notification, User, Tenant } from "@/types/api";

function useList<T>(key: string, url: string, params?: Record<string, unknown>) {
  return useQuery<PaginatedResponse<T>>({
    queryKey: [key, params],
    queryFn: async () => { const res = await api.get(url, { params }); return res.data; },
  });
}

function useDetail<T>(key: string, url: string) {
  return useQuery<T>({
    queryKey: [key],
    queryFn: async () => { const res = await api.get(url); return res.data; },
  });
}

function useCreate<T>(key: string, url: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<T>) => api.post(url, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: [key] }),
  });
}

function useUpdate<T>(key: string, url: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<T> }) => api.patch(`${url}${id}/`, data).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: [key] }),
  });
}

function useDelete(url: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.delete(`${url}${id}/`),
    onSuccess: () => qc.invalidateQueries(),
  });
}

export function useCustomers(params?: Record<string, unknown>) { return useList<Customer>("customers", "/customers/", params); }
export function useCustomer(id: string) { return useDetail<Customer>("customer", `/customers/${id}/`); }
export function useCreateCustomer() { return useCreate<Customer>("customers", "/customers/"); }
export function useUpdateCustomer() { return useUpdate<Customer>("customers", "/customers/"); }
export function useDeleteCustomer() { return useDelete("/customers/"); }

export function usePolicies(params?: Record<string, unknown>) { return useList<Policy>("policies", "/policies/", params); }
export function usePolicy(id: string) { return useDetail<Policy>("policy", `/policies/${id}/`); }
export function useCreatePolicy() { return useCreate<Policy>("policies", "/policies/"); }
export function useUpdatePolicy() { return useUpdate<Policy>("policies", "/policies/"); }
export function useDeletePolicy() { return useDelete("/policies/"); }

export function useClaims(params?: Record<string, unknown>) { return useList<Claim>("claims", "/claims/", params); }
export function useClaim(id: string) { return useDetail<Claim>("claim", `/claims/${id}/`); }
export function useCreateClaim() { return useCreate<Claim>("claims", "/claims/"); }
export function useUpdateClaim() { return useUpdate<Claim>("claims", "/claims/"); }

export function useQuotes(params?: Record<string, unknown>) { return useList<Quote>("quotes", "/quotes/", params); }
export function useQuote(id: string) { return useDetail<Quote>("quote", `/quotes/${id}/`); }
export function useCreateQuote() { return useCreate<Quote>("quotes", "/quotes/"); }

export function usePayments(params?: Record<string, unknown>) { return useList<Payment>("payments", "/payments/", params); }
export function usePayment(id: string) { return useDetail<Payment>("payment", `/payments/${id}/`); }

export function useProducts(params?: Record<string, unknown>) { return useList<Product>("products", "/products/", params); }
export function useProduct(id: string) { return useDetail<Product>("product", `/products/${id}/`); }

export function useAgents(params?: Record<string, unknown>) { return useList<Agent>("agents", "/agents/", params); }
export function useAgent(id: string) { return useDetail<Agent>("agent", `/agents/${id}/`); }

export function useBrokers(params?: Record<string, unknown>) { return useList<Broker>("brokers", "/brokers/", params); }
export function useBroker(id: string) { return useDetail<Broker>("broker", `/brokers/${id}/`); }

export function useDealers(params?: Record<string, unknown>) { return useList<Dealer>("dealers", "/dealers/", params); }
export function useDealer(id: string) { return useDetail<Dealer>("dealer", `/dealers/${id}/`); }

export function useBranches(params?: Record<string, unknown>) { return useList<Branch>("branches", "/branches/", params); }
export function useBranch(id: string) { return useDetail<Branch>("branch", `/branches/${id}/`); }

export function useAuditLogs(params?: Record<string, unknown>) { return useList<AuditLog>("audit", "/audit/", params); }
export function useNotifications(params?: Record<string, unknown>) { return useList<Notification>("notifications", "/notifications/", params); }
export function useUsers(params?: Record<string, unknown>) { return useList<User>("users", "/users/", params); }
export function useTenants(params?: Record<string, unknown>) { return useList<Tenant>("tenants", "/tenants/", params); }
