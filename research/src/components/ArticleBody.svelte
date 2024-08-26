<script lang="ts">
    import { onMount } from 'svelte'

    export let content: string
</script>

<div
    class="text-red
    max-w-screen-lg m-auto flex flex-col gap-y-4 mb-32 dark:text-white
    [&>p>a]:text-green-900 [&>p>a]:font-semibold
    [&>h1]:text-3xl [&>h2]:text-2xl [&>h3]:text-xl [&>h4]:text-lg [&>h1]:font-semibold
    [&>h2]:font-semibold [&>h3]:font-semibold [&>h4]:font-semibold
    [&>ul]:list-disc [&>ol]:list-decimal [&>ul]:pl-6 [&>ol>li]:pl-4 [&>ol]:pl-6
    [&>ul>li>ul]:list-disc [&>ul>li>ul]:pl-8 [&>ul>li>ul>li>ul]:list-disc [&>ul>li>ul>li>ul]:pl-8
    [&>ul>li>ul>li>ul>li>ul]:list-disc [&>ul>li>ul>li>ul>li>ul]:pl-8
    [&>p>em]:text-gray-200 [&>p>em]:text-center [&>p>img]:mx-auto [&>p>img]:mt-4 [&>p:has(img)]:text-center
    [&>p>em>img]:mx-auto [&>p>em>img]:mt-4 [&>h3>img]:mx-auto [&>h3:has(img)]:text-center
    [&>pre]:bg-gray [&>pre]:text-white [&>pre]:rounded-md [&>pre]:p-4 [&>pre]:overflow-x-scroll
    [&>pre>code>.hljs-string]:text-[#d69d85] [&>pre>code>.hljs-literal]:text-[#569cd6] [&>pre>code>.hljs-comment]:text-[#a2a8ad]
    [&>pre>code>.hljs-keyword]:text-[#d69d85]
    "
>
    {@html content}
</div>
