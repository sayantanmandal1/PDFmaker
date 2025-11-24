'use client';

import React from 'react';
import { useToast } from '@/contexts/ToastContext';
import { ToastContainer } from './ToastContainer';

export function ClientToastContainer() {
  const { toasts, removeToast } = useToast();

  return <ToastContainer toasts={toasts} onClose={removeToast} />;
}
