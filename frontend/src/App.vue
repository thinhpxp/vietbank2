<template>
  <div id="app">
    <!-- Thanh điều hướng chung -->
    <nav class="navbar">
      <div class="brand">Vietbank Contract App</div>
      <div class="links">
        <router-link to="/">Danh sách Hồ sơ</router-link> |
        <router-link to="/create">Tạo Hồ sơ Mới</router-link>
      </div>
    </nav>

    <!-- Nơi nội dung của từng trang sẽ hiển thị -->
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* CSS cơ bản cho đẹp */
body { margin: 0; background-color: #f4f6f8; font-family: sans-serif; }
#app { text-align: center; color: #2c3e50; }
.navbar { background: #2c3e50; padding: 15px; color: white; display: flex; justify-content: space-between; align-items: center; }
.brand { font-weight: bold; font-size: 1.2rem; }
.links a { color: #ecf0f1; text-decoration: none; margin: 0 10px; }
.links a.router-link-active { color: #42b983; font-weight: bold; }
</style>