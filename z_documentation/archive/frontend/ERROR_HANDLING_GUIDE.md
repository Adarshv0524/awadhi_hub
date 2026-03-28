# Error & State Handling Guide

## Overview
Production-grade error handling with friendly UI, rate-limit feedback, and global error boundary.

## Error Pages

### 404 - Not Found (`/404`)
- Large gradient "404" display
- Helpful message
- Quick navigation (Home, Search, Browse)
- Contact link

### 403 - Access Denied (`/403`)
- Orange/red gradient "403"
- Permission explanation
- Login button
- Help text for requesting access

### 500 - Server Error (`/500`)
- Red/pink gradient "500"
- Status indicator (pulsing dot)
- Reload and home buttons
- Support contact link

## Components

### ErrorBoundary.svelte
Global error boundary that catches unhandled errors and promise rejections.

**Auto-integrated in BaseLayout** - no manual setup needed!

**Features:**
- Catches global `error` and `unhandledrejection` events
- Modal overlay with error details
- Reload or dismiss actions
- Dev-only stack trace display

### RateLimitFeedback.svelte
Toast notification for rate limit errors with countdown.

**Usage:**
```svelte
<script>
  import RateLimitFeedback from "../components/RateLimitFeedback.svelte";
  import { parseRateLimitError } from "../lib/errorHandler";
  
  let showRateLimit = false;
  let retryAfter = null;
  
  async function makeRequest() {
    try {
      await api("/some/endpoint");
    } catch (e) {
      const rateLimitInfo = parseRateLimitError(e);
      if (rateLimitInfo?.isRateLimited) {
        showRateLimit = true;
        retryAfter = rateLimitInfo.retryAfter;
      }
    }
  }
</script>

<RateLimitFeedback 
  bind:show={showRateLimit} 
  {retryAfter}
  message="Too many search requests. Please wait."
/>
```

### ErrorDisplay.svelte
Inline error display component for consistent error UI.

**Usage:**
```svelte
<script>
  import ErrorDisplay from "../components/ErrorDisplay.svelte";
  let error = "Something went wrong";
</script>

<ErrorDisplay 
  {error}
  type="error"
  title="Request Failed"
  dismissible={true}
  action={{ label: "Retry", onClick: () => retry() }}
/>
```

**Props:**
- `error: string | null` - Error message
- `type: "error" | "warning" | "info"` - Visual style
- `title: string | null` - Optional title
- `action: { label, onClick }` - Optional action button
- `dismissible: boolean` - Show dismiss button
- `onDismiss: () => void` - Dismiss callback

## Error Handler Utilities

### `errorHandler.ts`

**parseRateLimitError(error)**
```typescript
const info = parseRateLimitError(error);
if (info?.isRateLimited) {
  // Show rate limit UI
  // info.retryAfter = seconds to wait
  // info.message = user-friendly message
}
```

**handleApiError(error)**
```typescript
const { message, shouldRedirect, redirectUrl } = handleApiError(error);
if (shouldRedirect && redirectUrl) {
  window.location.href = redirectUrl;
}
```

**Helper functions:**
- `isNetworkError(error)` - Check for network failures
- `isForbiddenError(error)` - Check for 403
- `isNotFoundError(error)` - Check for 404
- `isServerError(error)` - Check for 5xx
- `getErrorMessage(error)` - Extract user-friendly message

## Best Practices

### 1. Use ApiError checks
```typescript
import { ApiError } from "../lib/api";
import { isNotFoundError } from "../lib/errorHandler";

try {
  const data = await api("/endpoint");
} catch (e) {
  if (isNotFoundError(e)) {
    return Astro.redirect("/404");
  }
  error = getErrorMessage(e);
}
```

### 2. Handle rate limits gracefully
```typescript
import { parseRateLimitError } from "../lib/errorHandler";

const rateLimitInfo = parseRateLimitError(error);
if (rateLimitInfo?.isRateLimited) {
  // Show RateLimitFeedback component
  // Disable submit buttons
  // Show countdown
}
```

### 3. Provide user actions
```svelte
<ErrorDisplay 
  error="Failed to save"
  action={{ label: "Try Again", onClick: retry }}
/>
```

### 4. Redirect on auth errors
```typescript
if (isForbiddenError(error)) {
  window.location.href = "/login?redirect=" + encodeURIComponent(window.location.pathname);
}
```

## What We Avoided (No Feature Creep)
❌ No retry queues (just simple retry buttons)
❌ No offline banners (not needed for this app)
❌ No request interceptors (keep it simple)
❌ No error analytics (future consideration)

## Integration Examples

### Search Page
```svelte
<script>
  import ErrorDisplay from "../components/ErrorDisplay.svelte";
  import RateLimitFeedback from "../components/RateLimitFeedback.svelte";
  import { parseRateLimitError } from "../lib/errorHandler";
  
  let error = null;
  let showRateLimit = false;
  let retryAfter = null;
  
  async function search() {
    try {
      error = null;
      const results = await api("/search?q=" + query);
    } catch (e) {
      const rateLimitInfo = parseRateLimitError(e);
      if (rateLimitInfo?.isRateLimited) {
        showRateLimit = true;
        retryAfter = rateLimitInfo.retryAfter;
      } else {
        error = getErrorMessage(e);
      }
    }
  }
</script>

<ErrorDisplay {error} type="error" dismissible />
<RateLimitFeedback bind:show={showRateLimit} {retryAfter} />
```

### Form Submission
```svelte
<script>
  import ErrorDisplay from "../components/ErrorDisplay.svelte";
  import { handleApiError } from "../lib/errorHandler";
  
  let error = null;
  
  async function submit() {
    try {
      await api("/submit", { method: "POST", body: formData });
      window.location.href = "/success";
    } catch (e) {
      const { message, shouldRedirect, redirectUrl } = handleApiError(e);
      if (shouldRedirect && redirectUrl) {
        window.location.href = redirectUrl;
      } else {
        error = message;
      }
    }
  }
</script>

<ErrorDisplay 
  {error}
  title="Submission Failed"
  action={{ label: "Retry", onClick: submit }}
/>
```
