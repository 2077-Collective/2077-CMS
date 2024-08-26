<script lang="ts">
    import ChevronUp from './icons/ChevronUp.svelte'
</script>

<button
    class="bg-gray-100 rounded-full opacity-40 hover:opacity-80 p-2 fixed bottom-5 right-5 lg:bottom-10 lg:right-10"
    on:click={() => window.scrollTo(0, 0)}
>
    <ChevronUp size="16px" />
</button>
