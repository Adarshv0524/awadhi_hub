<script>
  export let apiBase = "";

  import { onMount } from "svelte";
  import { getUsers, updateUser } from "../../lib/admin";

  let users = [];
  let filteredUsers = [];
  let loading = true;
  let error = "";
  let info = "";
  let currentPage = 1;
  let pageSize = 50;
  let query = "";
  let roleFilter = "all";
  let statusFilter = "all";
  let editingUser = null;
  let showPermissionsModal = false;
  let scopeEditorText = "{}";
  const editableRoles = ["guest", "registered", "moderator", "senior_moderator", "admin"];

  async function load() {
    loading = true;
    error = "";
    info = "";
    try {
      const offset = (currentPage - 1) * pageSize;
      users = await getUsers(pageSize, offset, apiBase);
    } catch (e) {
      error = e.message || String(e);
    } finally {
      loading = false;
    }
  }

  async function quickUpdate(userId, field, value) {
    error = "";
    try {
      await updateUser(userId, { [field]: value }, apiBase);
      info = "User updated successfully.";
      await load();
    } catch (e) {
      error = String(e);
    }
  }

  function openPermissions(user) {
    editingUser = { ...user };
    scopeEditorText = JSON.stringify(user.permission_scopes || {}, null, 2);
    showPermissionsModal = true;
    error = "";
  }

  function closePermissions() {
    editingUser = null;
    showPermissionsModal = false;
    scopeEditorText = "{}";
  }

  async function savePermissions() {
    if (!editingUser) return;
    let parsedScopes = {};

    try {
      parsedScopes = scopeEditorText.trim() ? JSON.parse(scopeEditorText) : {};
    } catch {
      error = "Permission scopes must be valid JSON.";
      return;
    }

    try {
      await updateUser(editingUser.id, {
        role: editingUser.role,
        permissions: Number(editingUser.permissions || 0),
        permission_scopes: parsedScopes,
        is_active: editingUser.is_active,
        is_banned: editingUser.is_banned || false
      }, apiBase);
      closePermissions();
      info = "User permissions saved.";
      await load();
    } catch (e) {
      error = String(e);
    }
  }

  function nextPage() {
    if (users.length === pageSize) {
      currentPage++;
      load();
    }
  }

  function prevPage() {
    if (currentPage > 1) {
      currentPage--;
      load();
    }
  }

  function exportCsv() {
    const rows = [
      ["id", "username", "email", "role", "active", "banned", "permissions", "created_at"],
      ...filteredUsers.map((u) => [
        String(u.id),
        String(u.username ?? ""),
        String(u.email ?? ""),
        String(u.role ?? ""),
        String(Boolean(u.is_active)),
        String(Boolean(u.is_banned)),
        String(u.permissions ?? 0),
        String(u.created_at ?? ""),
      ]),
    ];

    const csv = rows.map((row) => row.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `admin_users_page_${currentPage}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function clearFilters() {
    query = "";
    roleFilter = "all";
    statusFilter = "all";
  }

  function applyFilters(list) {
    const q = query.trim().toLowerCase();
    return list.filter((u) => {
      const matchesQuery =
        !q ||
        String(u.email || "").toLowerCase().includes(q) ||
        String(u.username || "").toLowerCase().includes(q) ||
        String(u.id).includes(q);

      const matchesRole = roleFilter === "all" || u.role === roleFilter;

      const matchesStatus =
        statusFilter === "all" ||
        (statusFilter === "active" && u.is_active) ||
        (statusFilter === "inactive" && !u.is_active) ||
        (statusFilter === "banned" && u.is_banned);

      return matchesQuery && matchesRole && matchesStatus;
    });
  }

  function onDialogEsc(event) {
    if (event.key === "Escape" && showPermissionsModal) {
      closePermissions();
    }
  }

  $: filteredUsers = applyFilters(users);

  onMount(load);
</script>

<svelte:window on:keydown={onDialogEsc} />

{#if loading}
  <p role="status" aria-live="polite">Loading users...</p>
{:else}
  {#if info}
    <p class="mb-3 admin-state-ok" role="status" aria-live="polite">{info}</p>
  {/if}
  {#if error}
    <div class="mb-4 rounded border border-rose-500/30 bg-rose-900/15 p-3 text-rose-200" role="alert" aria-live="assertive">
      <p class="font-semibold">Could not load users</p>
      <p class="text-sm mt-1">{error}</p>
      <button class="mt-3 admin-btn admin-btn-danger" on:click={load}>Retry</button>
    </div>
  {:else}
    <div class="mb-4 grid gap-3 md:grid-cols-12 md:items-end">
      <div class="md:col-span-4">
        <label for="users-search" class="block text-sm mb-1">Search</label>
        <input id="users-search" class="w-full" type="search" bind:value={query} placeholder="Search by id, username, or email" />
      </div>
      <div class="md:col-span-2">
        <label for="users-role-filter" class="block text-sm mb-1">Role</label>
        <select id="users-role-filter" bind:value={roleFilter} class="w-full">
          <option value="all">All roles</option>
          <option value="guest">Guest</option>
          <option value="registered">Registered</option>
          <option value="moderator">Moderator</option>
          <option value="senior_moderator">Senior Moderator</option>
          <option value="admin">Admin</option>
          <option value="contributor">Contributor (legacy)</option>
        </select>
      </div>
      <div class="md:col-span-2">
        <label for="users-status-filter" class="block text-sm mb-1">Status</label>
        <select id="users-status-filter" bind:value={statusFilter} class="w-full">
          <option value="all">All statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="banned">Banned</option>
        </select>
      </div>
      <div class="md:col-span-2">
        <label for="users-page-size" class="block text-sm mb-1">Page size</label>
        <select
          id="users-page-size"
          bind:value={pageSize}
          class="w-full"
          on:change={() => {
            currentPage = 1;
            load();
          }}
        >
          <option value={25}>25</option>
          <option value={50}>50</option>
          <option value={100}>100</option>
        </select>
      </div>
      <div class="md:col-span-2 flex gap-2 justify-end">
        <button on:click={clearFilters} class="admin-btn">Clear</button>
        <button on:click={exportCsv} class="admin-btn" aria-label="Export current filtered users to CSV">Export CSV</button>
        <button on:click={load} class="admin-btn admin-btn-primary">Refresh</button>
      </div>
    </div>

    <div class="mb-3 flex justify-between items-center">
      <div class="text-sm" role="status" aria-live="polite">
        Page {currentPage} | {filteredUsers.length} users shown
      </div>
      <div class="flex gap-2">
        <button
          on:click={prevPage}
          disabled={currentPage === 1}
          class="admin-btn disabled:opacity-50"
          aria-label="Previous users page"
        >
          Previous
        </button>
        <button
          on:click={nextPage}
          disabled={users.length < pageSize}
          class="admin-btn disabled:opacity-50"
          aria-label="Next users page"
        >
          Next
        </button>
      </div>
    </div>

    <table class="w-full border-collapse" aria-label="Admin users table">
      <caption class="sr-only">Manage users, roles, permissions, and account state</caption>
      <thead>
        <tr class="text-left">
          <th scope="col" class="py-2 px-2">ID</th>
          <th scope="col" class="px-2">Email / Username</th>
          <th scope="col" class="px-2">Role</th>
          <th scope="col" class="px-2">State</th>
          <th scope="col" class="px-2">Created</th>
          <th scope="col" class="px-2">Actions</th>
        </tr>
      </thead>
      <tbody>
        {#if filteredUsers.length === 0}
          <tr class="border-t">
            <td colspan="6" class="py-4 px-2 text-sm text-slate-400">No users match the current filters.</td>
          </tr>
        {:else}
        {#each filteredUsers as u}
          <tr class="border-t">
            <td class="py-2 px-2">{u.id}</td>
            <td class="px-2">
              <div class="font-medium">{u.username ?? "—"}</div>
              <div class="text-sm text-slate-400">{u.email}</div>
            </td>
            <td class="px-2">
              <label class="sr-only" for={`role-${u.id}`}>Role for user {u.id}</label>
              <select
                id={`role-${u.id}`}
                on:change={(e) => quickUpdate(u.id, 'role', e.target.value)} 
                value={u.role} 
                class="bg-transparent border rounded px-2 py-1"
              >
                {#if !editableRoles.includes(u.role)}
                  <option value={u.role}>{u.role} (legacy)</option>
                {/if}
                <option value="guest">guest</option>
                <option value="registered">registered</option>
                <option value="moderator">moderator</option>
                <option value="senior_moderator">senior_moderator</option>
                <option value="admin">admin</option>
              </select>
            </td>
            <td class="px-2">
              <div class="space-y-1">
              <label class="inline-flex items-center cursor-pointer mr-3">
                <input 
                  type="checkbox" 
                  checked={u.is_active} 
                  on:change={(e) => quickUpdate(u.id, 'is_active', e.target.checked)}
                  class="mr-2"
                />
                <span class={u.is_active ? 'admin-state-ok' : 'admin-state-bad'}>
                  {u.is_active ? 'Active' : 'Inactive'}
                </span>
              </label>
              <label class="inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={Boolean(u.is_banned)}
                  on:change={(e) => quickUpdate(u.id, 'is_banned', e.target.checked)}
                  class="mr-2"
                />
                <span class={u.is_banned ? 'admin-state-bad' : 'text-slate-400'}>
                  {u.is_banned ? 'Banned' : 'Not banned'}
                </span>
              </label>
              </div>
            </td>
            <td class="text-sm text-slate-400 px-2">{u.created_at ? new Date(u.created_at).toLocaleString() : "-"}</td>
            <td class="px-2">
              <button
                class="text-slate-300 text-sm hover:underline"
                on:click={() => openPermissions(u)}
                aria-label={`Manage permissions for user ${u.id}`}
              >
                Manage
              </button>
            </td>
          </tr>
        {/each}
        {/if}
      </tbody>
    </table>
  {/if}
{/if}

<!-- Permissions Modal -->
{#if showPermissionsModal && editingUser}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
    <button class="absolute inset-0" aria-label="Close dialog" on:click={closePermissions}></button>
    <div class="relative bg-slate-900 border border-slate-600 rounded-xl p-6 max-w-lg mx-4 shadow-2xl" role="dialog" aria-modal="true" aria-label="Manage user permissions">
      <h3 class="text-xl font-bold text-slate-100 mb-4">Manage User: {editingUser.username || editingUser.email}</h3>
      
      <div class="space-y-4">
        <!-- Role -->
        <div>
          <label for="edit-role" class="block text-sm font-medium text-slate-300 mb-2">Role</label>
          <select 
            id="edit-role"
            bind:value={editingUser.role} 
            class="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-slate-200"
          >
              <option value="guest">Guest</option>
            <option value="registered">Registered</option>
            <option value="moderator">Moderator</option>
              <option value="senior_moderator">Senior Moderator</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        <div>
          <label for="edit-permissions" class="block text-sm font-medium text-slate-300 mb-2">Permission bitmask</label>
          <input
            id="edit-permissions"
            type="number"
            min="0"
            bind:value={editingUser.permissions}
            class="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-slate-200"
          />
          <p class="text-xs text-slate-500 mt-1">Use integer bitmask (example: 1=manage users, 2=moderate, 4=view audit, 8=manage settings).</p>
        </div>

        <div>
          <label for="edit-scopes" class="block text-sm font-medium text-slate-300 mb-2">Permission scopes (JSON)</label>
          <textarea
            id="edit-scopes"
            bind:value={scopeEditorText}
            rows="5"
            class="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-slate-200 font-mono text-xs"
          ></textarea>
        </div>

        <!-- Active Status -->
        <div>
          <label class="inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              bind:checked={editingUser.is_active}
              class="mr-3 w-4 h-4"
            />
            <span class="text-slate-300">Account Active</span>
          </label>
          <p class="text-xs text-slate-500 mt-1">Inactive users cannot log in</p>
        </div>

        <!-- Banned Status -->
        <div>
          <label class="inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              bind:checked={editingUser.is_banned}
              class="mr-3 w-4 h-4"
            />
            <span class="text-slate-300">Banned</span>
          </label>
          <p class="text-xs text-slate-500 mt-1">Banned users are permanently blocked</p>
        </div>

        <!-- Info Box -->
        <div class="bg-slate-900/70 border border-slate-700 rounded p-3 text-xs text-slate-300">
          <p class="mb-1"><strong>Tip:</strong> Changes apply immediately.</p>
          <p>Keep at least one active admin account with settings access.</p>
        </div>
      </div>

      <div class="flex gap-3 justify-end mt-6">
        <button
          on:click={closePermissions}
          class="admin-btn"
        >
          Cancel
        </button>
        <button
          on:click={savePermissions}
          class="admin-btn admin-btn-primary"
        >
          Save Changes
        </button>
      </div>
    </div>
  </div>
{/if}
