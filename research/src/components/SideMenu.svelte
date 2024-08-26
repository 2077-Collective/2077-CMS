<script lang="ts">
    import { type Article } from '../types/article'
    import {
        setCategory,
        clearCategories,
        category,
    } from '../stores/filters.store'

    export let articles: Article[]
    let availableCategories: string[] = []

    $: {
        availableCategories = Array.from(
            new Set(
                articles.flatMap((article) =>
                    article.categories.map((category) => category.name),
                ),
            ),
        )
    }
</script>

<div
    class="hidden menu lg:block lg:min-w-[180px] mr-12 rounded-md xl:w-1/6 h-[520px]"
>
    <div class="font-bold pt-2 px-2 flex-col">
        <button
            class="block px-4 py-4 transition-all"
            on:click={() => clearCategories()}
        >
            <span
                class="font-sans hover:underline"
                class:font-medium={$category}
                class:text-gray-200={$category}
                class:dark:font-thin={$category}>All</span
            >
        </button>

        {#each availableCategories as articleCategory}
            <button
                class="block px-4 py-4 transition-all"
                on:click={() => setCategory(articleCategory)}
            >
                <span
                    class="font-sans hover:underline"
                    class:text-gray-200={$category !== articleCategory}
                    class:font-medium={$category !== articleCategory}
                    class:dark:font-thin={$category !== articleCategory}
                >
                    {articleCategory}
                </span>
            </button>
        {/each}
    </div>
</div>

<div class="flex flex-wrap gap-2 block lg:hidden mb-8">
    <button
        class="
            mr-2 font-bold flex items-center gap-0.5 text-sm bg-[#1B1B1B]
            text-gray-100 min-w-fit px-2 py-1.5 rounded-md hover:text-green
            hover:bg-black text-left
        "
        class:text-green={!$category}
        on:click={() => clearCategories()}
    >
        All
    </button>
    {#each availableCategories as articleCategory}
        <button
            class="
                mr-2 font-bold flex items-center gap-0.5 text-sm bg-[#1B1B1B]
                text-gray-100 min-w-fit px-2 py-1.5 rounded-md hover:text-green
                hover:bg-black
            "
            class:text-green={$category === articleCategory}
            on:click={() => setCategory(articleCategory)}
        >
            {articleCategory}
        </button>
    {/each}
</div>

<style scoped>
    .menu {
        clip-path: polygon(30px 0, 100% 0, 290% 20px, 85% 100%, 0 100%, 0 30px);
    }

    .menu > div > button {
        clip-path: polygon(30px 0, 100% 0, 110% 20px, 85% 100%, 0 100%, 0 30px);
    }
</style>
