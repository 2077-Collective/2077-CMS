<script lang="ts">
    import { setLoading } from '../stores/loader.store'

    export let path: string
</script>

<div
    class="mb-4"
    on:click={() => {
        if (window.location.pathname === path) {
            return
        }

        setLoading(true)
    }}
>
    <a href={path}>
        <slot name="label" />
    </a>
</div>
