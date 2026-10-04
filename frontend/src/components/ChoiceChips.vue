<template>
  <div class="flex flex-wrap gap-2" :role="multiple ? 'group' : 'radiogroup'">
    <button
      v-for="o in options"
      :key="o.id"
      type="button"
      class="chip"
      :class="{ on: isOn(o) }"
      :aria-pressed="multiple ? isOn(o) : undefined"
      :aria-checked="multiple ? undefined : isOn(o)"
      @click="toggle(o)"
    >
      <slot name="item" :o="o">
        <AppIcon v-if="o.icon" :name="o.icon" />
        <span>{{ o.label }}</span>
      </slot>
    </button>
  </div>
</template>

<script setup>
import AppIcon from './AppIcon.vue'

const props = defineProps({
  options: { type: Array, default: () => [] },
  modelValue: { type: [String, Array], default: '' },
  multiple: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

function isOn(o) {
  if (props.multiple) return Array.isArray(props.modelValue) && props.modelValue.includes(o.id)
  return props.modelValue === o.id
}

function toggle(o) {
  if (props.multiple) {
    const cur = Array.isArray(props.modelValue) ? [...props.modelValue] : []
    const i = cur.indexOf(o.id)
    if (i >= 0) cur.splice(i, 1)
    else cur.push(o.id)
    emit('update:modelValue', cur)
  } else {
    emit('update:modelValue', o.id)
  }
}
</script>
