'use client';

import type {
  ButtonHTMLAttributes,
  HTMLAttributes,
  InputHTMLAttributes,
  SelectHTMLAttributes,
  ReactNode,
} from 'react';
import type { StationStatus } from '@/lib/types';

// Une clases condicionales de forma simple.
function cx(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(' ');
}

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

export function Button({
  variant = 'primary',
  className,
  ...props
}: ButtonProps) {
  const base =
    'inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-1';
  const variants: Record<ButtonVariant, string> = {
    primary:
      'text-white hover:opacity-90 focus:ring-[var(--primary)] bg-[var(--primary)]',
    secondary:
      'bg-white text-gray-800 border border-gray-300 hover:bg-gray-50 focus:ring-gray-300',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    ghost: 'text-gray-600 hover:bg-gray-100 focus:ring-gray-300',
  };
  return (
    <button className={cx(base, variants[variant], className)} {...props} />
  );
}

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cx(
        'w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-[var(--primary)] focus:outline-none focus:ring-1 focus:ring-[var(--primary)]',
        className,
      )}
      {...props}
    />
  );
}

export function Select({
  className,
  children,
  ...props
}: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className={cx(
        'w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:border-[var(--primary)] focus:outline-none focus:ring-1 focus:ring-[var(--primary)]',
        className,
      )}
      {...props}
    >
      {children}
    </select>
  );
}

export function Label({ children, htmlFor }: { children: ReactNode; htmlFor?: string }) {
  return (
    <label htmlFor={htmlFor} className="mb-1 block text-sm font-medium text-gray-700">
      {children}
    </label>
  );
}

export function Card({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cx(
        'rounded-lg border border-gray-200 bg-white p-5 shadow-sm',
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}

// Tarjeta de KPI con título y valor destacado.
export function StatCard({ label, value }: { label: string; value: ReactNode }) {
  return (
    <Card className="flex flex-col gap-1">
      <span className="text-sm text-gray-500">{label}</span>
      <span className="text-2xl font-semibold text-gray-900">{value}</span>
    </Card>
  );
}

const statusLabels: Record<StationStatus, string> = {
  available: 'Disponible',
  occupied: 'Ocupada',
  offline: 'Fuera de línea',
  maintenance: 'Mantenimiento',
};

const statusStyles: Record<StationStatus, string> = {
  available: 'bg-green-100 text-green-800',
  occupied: 'bg-blue-100 text-blue-800',
  offline: 'bg-gray-200 text-gray-700',
  maintenance: 'bg-amber-100 text-amber-800',
};

export function StatusBadge({ status }: { status: StationStatus }) {
  return (
    <span
      className={cx(
        'inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium',
        statusStyles[status],
      )}
    >
      {statusLabels[status]}
    </span>
  );
}

export { statusLabels };
