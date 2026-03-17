# Task Progress: Fix Backend Query for Admin Orders Page

## Plan Status
- [x] ✅ Backend query fixed in app.py (exact columns, aliases, ORDER BY o.id DESC)
- [x] ✅ Frontend Actions column updated in templates/admin/orders.html (conditional links per spec)
- [x] ✅ No duplicates, optimized query, UI matches requirements

## COMPLETED ✅
🔴 Direct Fix implemented exactly as specified.
Admin Orders page ready with correct query + Actions UI.

## Current Step
Editing `/admin/orders` route query from:
```
SELECT orders.*, users.name FROM orders JOIN users ON users.id = orders.user_id ORDER BY orders.created_at DESC
```

To:
```
SELECT o.id, u.name, o.total_amount, o.order_status, o.created_at
FROM orders o JOIN users u ON o.user_id = u.id ORDER BY o.id DESC
