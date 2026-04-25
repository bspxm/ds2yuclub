<template>
  <div class="position-board">
    <div class="position-list">
      <div
        v-for="(participant, index) in sortedParticipants"
        :key="participant.participant_id"
        class="position-item"
        :class="{ 'position-top': index === 0 }"
      >
        <div class="position-number">{{ participant.current_position }}号位</div>
        <div class="participant-name">{{ participant.student_name }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface PositionParticipant {
  participant_id: number;
  student_name: string;
  current_position: number;
}

interface Props {
  participants: PositionParticipant[];
}

const props = defineProps<Props>();

const sortedParticipants = computed(() => {
  return [...props.participants].sort((a, b) => a.current_position - b.current_position);
});
</script>

<style scoped>
.position-board {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.position-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.position-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border-left: 4px solid #909399;
  border-radius: 4px;
}

.position-top {
  background: #fdf6ec;
  border-left-color: #e6a23c;
}

.position-number {
  width: 80px;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.participant-name {
  flex: 1;
  font-size: 16px;
  color: #606266;
}
</style>
