# Common Components - Error Handling & Loading States

This directory contains reusable components for error handling, loading states, and user notifications.

## Components

### ErrorBoundary
React Error Boundary component that catches JavaScript errors anywhere in the component tree.

**Usage:**
```tsx
import { ErrorBoundary } from '@/components/common';

<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>
```

**Features:**
- Catches runtime errors in child components
- Displays user-friendly error message
- Provides "Try Again" and "Go to Dashboard" actions
- Logs errors to console for debugging

### Toast Notifications
Toast notification system for displaying temporary success/error/info/warning messages.

**Usage:**
```tsx
import { useToast } from '@/contexts/ToastContext';

function MyComponent() {
  const { showSuccess, showError, showInfo, showWarning } = useToast();
  
  const handleAction = async () => {
    try {
      await someAction();
      showSuccess('Action completed successfully!');
    } catch (error) {
      showError('Action failed. Please try again.');
    }
  };
}
```

**Toast Types:**
- `showSuccess(message, duration?)` - Green success toast
- `showError(message, duration?)` - Red error toast
- `showInfo(message, duration?)` - Blue info toast
- `showWarning(message, duration?)` - Yellow warning toast

**Default Duration:** 5000ms (5 seconds)

### LoadingSpinner
Spinner component for indicating loading states.

**Usage:**
```tsx
import { LoadingSpinner, LoadingOverlay, LoadingState } from '@/components/common';

// Inline spinner
<LoadingSpinner size="sm" label="Loading..." />

// Full-screen overlay
<LoadingOverlay message="Processing..." />

// Centered loading state
<LoadingState message="Loading data..." />
```

**Sizes:** `sm`, `md`, `lg`, `xl`

### ErrorMessage
Component for displaying error messages with optional retry action.

**Usage:**
```tsx
import { ErrorMessage, InlineError } from '@/components/common';

// Full error message with retry
<ErrorMessage 
  message="Failed to load data"
  title="Error"
  onRetry={handleRetry}
/>

// Inline error (compact)
<InlineError message="Invalid input" />
```

### EmptyState
Component for displaying empty states with optional action button.

**Usage:**
```tsx
import { EmptyState } from '@/components/common';

<EmptyState
  title="No projects yet"
  message="Get started by creating your first project"
  action={{
    label: "Create Project",
    onClick: handleCreate
  }}
/>
```

## Best Practices

### Error Handling
1. Always wrap async operations in try-catch blocks
2. Use toast notifications for user feedback
3. Display inline errors for form validation
4. Use ErrorBoundary at page/route level
5. Log errors to console for debugging

### Loading States
1. Show loading spinners for async operations
2. Disable buttons during loading
3. Use aria-busy attribute for accessibility
4. Provide meaningful loading messages

### Network Errors
The API client automatically handles network errors and returns structured ApiError objects:
```tsx
try {
  await apiCall();
} catch (err) {
  const apiError = err as ApiError;
  showError(apiError.detail || 'Operation failed');
}
```

## Accessibility
All components follow accessibility best practices:
- Proper ARIA labels and roles
- Keyboard navigation support
- Screen reader announcements
- Focus management
