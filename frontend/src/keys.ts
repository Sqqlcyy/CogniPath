// /src/keys.ts
import type { InjectionKey, Ref } from 'vue';
import type MeteorShower from '@/components/common/MeteorShower.vue';

type MeteorShowerInstance = InstanceType<typeof MeteorShower>;

export const meteorShowerKey: InjectionKey<Ref<MeteorShowerInstance | null>> = Symbol('meteorShower');