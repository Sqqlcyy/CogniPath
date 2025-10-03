<template>
  <div class="app-container">
    <!-- 
      动态星空背景的实现。
      我们使用三个独立的div来创建三个不同速度和大小的星空层，
      从而营造出视差滚动的深邃感。
    -->
    <div class="stars-background">
      <div id="stars1"></div>
      <div id="stars2"></div>
      <div id="stars3"></div>
    </div>

    <!-- 
      路由视图。
      我们所有的页面 (UploadView, WorkspaceLayout等) 都会在这里被渲染。
      我们给它加上一个过渡效果，让页面切换更平滑。
    -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup lang="ts">
// 这个组件非常纯粹，不需要任何逻辑。
// 所有的状态和业务逻辑都由其子组件和Pinia Store处理。
</script>

<style lang="scss">
/* 
 * ===================================================================
 *  App.vue 专属样式 - 动态星空绘制
 *  这段SCSS代码就是我们的“画笔”。
 * ===================================================================
 */
 @use "sass:math";
 @use "sass:string";
// SCSS 辅助函数，用于生成随机的星星
@function random_range($min, $max) {
  $rand: random();
  $random_range: $min + floor($rand * ($max - $min + 1));
  @return $random_range;
}

// 星星的阴影效果是创建多个星星的关键
// 我们用一个循环来生成大量的、位置随机的星星
@function multiple-box-shadow($n) {
  $value: '#{random_range(0, 2000)}px #{random_range(0, 2000)}px #FFF';
  @for $i from 2 through $n {
    $value: '#{$value} , #{random_range(0, 2000)}px #{random_range(0, 2000)}px #FFF';
  }
  @return unquote($value);
}

// 定义不同层次的星星数量
$stars-small: 700;
$stars-medium: 200;
$stars-large: 100;

// 星空背景容器
.app-container {
  width: 100vw;
  height: 100vh;
  // 使用我们在main.scss中定义的深黑色背景
  background: var(--bg-color, #0C0C0C); 
  overflow: hidden;
  position: relative;
}

.stars-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0; // 确保在内容之下
}

// 每个星空层都是一个透明的div，星星是通过box-shadow绘制的
#stars1, #stars2, #stars3 {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 1px;
  height: 1px;
  background: transparent;
  // 动画效果
  animation-name: animStar;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
}

// 定义不同层次的星星大小和动画速度
#stars1 {
  box-shadow: multiple-box-shadow($stars-small);
  animation-duration: 50s; // 最近的星星，移动最快
}
#stars2 {
  // 中等大小的星星
  box-shadow: multiple-box-shadow($stars-medium);
  animation-duration: 100s; // 中间的星星，速度适中
}
#stars3 {
  // 最小的星星
  box-shadow: multiple-box-shadow($stars-large);
  animation-duration: 150s; // 最远的星星，移动最慢
}

// 定义星星移动的动画
@keyframes animStar {
  from {
    transform: translateY(0px);
  }
  to {
    transform: translateY(-2000px);
  }
}

// 页面切换的淡入淡出效果
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>