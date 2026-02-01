import { BinStatus } from '../types';
import { format, formatDistanceToNow } from 'date-fns';

// Get status color class
export function getStatusColor(status: BinStatus): string {
  const colors: Record<BinStatus, string> = {
    normal: 'bg-status-normal',
    low: 'bg-status-low',
    critical: 'bg-status-critical',
    empty: 'bg-status-empty',
    overfill: 'bg-status-overfill',
  };
  return colors[status] || colors.normal;
}

// Get status border color class
export function getStatusBorderColor(status: BinStatus): string {
  const colors: Record<BinStatus, string> = {
    normal: 'border-status-normal',
    low: 'border-status-low',
    critical: 'border-status-critical',
    empty: 'border-status-empty',
    overfill: 'border-status-overfill',
  };
  return colors[status] || colors.normal;
}

// Get status text color class
export function getStatusTextColor(status: BinStatus): string {
  const colors: Record<BinStatus, string> = {
    normal: 'text-status-normal',
    low: 'text-status-low',
    critical: 'text-status-critical',
    empty: 'text-status-empty',
    overfill: 'text-status-overfill',
  };
  return colors[status] || colors.normal;
}

// Get fill bar color based on percentage
export function getFillBarColor(percentage: number, status: BinStatus): string {
  if (status === 'overfill') return 'bg-status-overfill';
  if (percentage <= 10) return 'bg-status-empty';
  if (percentage <= 25) return 'bg-status-critical';
  if (percentage <= 50) return 'bg-status-low';
  return 'bg-status-normal';
}

// Format timestamp for display
export function formatTimestamp(timestamp: string): string {
  try {
    return format(new Date(timestamp), 'MMM d, yyyy HH:mm:ss');
  } catch {
    return timestamp;
  }
}

// Format relative time
export function formatRelativeTime(timestamp: string): string {
  try {
    return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
  } catch {
    return timestamp;
  }
}

// Format number with commas
export function formatNumber(num: number): string {
  return num.toLocaleString();
}

// Clamp number between min and max
export function clamp(num: number, min: number, max: number): number {
  return Math.min(Math.max(num, min), max);
}

// Generate ISO date string for today
export function getTodayISO(): string {
  return new Date().toISOString();
}

// Generate ISO date string for days ago
export function getDaysAgoISO(days: number): string {
  const date = new Date();
  date.setDate(date.getDate() - days);
  return date.toISOString();
}

// Debounce function
export function debounce<T extends (...args: unknown[]) => void>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Download file from URL
export function downloadFile(url: string, filename?: string): void {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename || '';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
