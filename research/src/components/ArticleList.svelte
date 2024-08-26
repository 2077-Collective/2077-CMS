<script lang="ts">
    import { type Article } from '../types/article'
    import { category } from '../stores/filters.store'

    export let articles: Article[]
    let filteredArticles: Article[]

    $: {
        if ($category === undefined) {
            filteredArticles = articles
        } else {
            filteredArticles = articles.filter((article) =>
                article.categories.some(
                    (articleCategory) => $category === articleCategory.name,
                ),
            )
        }
    }
</script>

<ul
    class="mb-32 grid sm:grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-x-12 gap-y-10 xl:w-5/6"
>
    {#each filteredArticles as article (article.id)}
        <li class="flex flex-col gap-y-1 group cursor-pointer">
            <a class="bg-transparent" href={`/${article.slug}`}>
                <img
                    src={article.thumb}
                    alt=""
                    width="720"
                    height="480"
                    class="group-hover:opacity-80 dark:group-hover:opacity-50 transition-opacity"
                />
                <ul class="flex py-2">
                    {#each article.categories as category}
                        <li class="">
                            <a
                                href={`/categories/${category.name}`}
                                class="mr-2 flex items-center gap-0.5 text-[12px] bg-[#1B1B1B] text-[#C6FF50] max-w-fit-content px-2 py-1 rounded-md"
                            >
                                {category.name}
                            </a>
                        </li>
                    {/each}
                </ul>
                <h2
                    class="mb-2 text-md font-semibold underline decoration-white dark:decoration-black group-hover:decoration-black dark:group-hover:decoration-white transition-colors leading-5"
                >
                    {article.title}
                </h2>
                <p class="text-sm text-gray-900 font-bold leading-17">
                    {article.summary}
                </p>
            </a>
        </li>
    {/each}
</ul>
