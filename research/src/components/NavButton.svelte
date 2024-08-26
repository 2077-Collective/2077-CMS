<script lang="ts">
    import { setLoading } from '../stores/loader.store'

    export let path: string
</script>

<div class="mb-4" on:click={() => setLoading(true)}>
    <a href={path}>
        <slot name="label" />
    </a>
</div>
