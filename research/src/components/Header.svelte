<script lang="ts">
    import MobileNav from './MobileNav.svelte'
    import Dropdown from './Dropdown.svelte'
    import ToggleTheme from './ToggleTheme.svelte'
</script>

<header class="py-8 px-6 lg:px-32 max-w-screen-3xl m-auto w-full">
    <nav class="flex justify-between">
        <div>
            <a href="/">
                <img
                    src="/logo-black.webp"
                    alt=""
                    width="197"
                    height="58"
                    class="dark:hidden block"
                />
                <img
                    src="/logo-white.webp"
                    alt=""
                    width="197"
                    height="58"
                    class="dark:block hidden"
                />
            </a>
        </div>

        <div class="flex items-center gap-0 md:gap-2 lg:gap-4">
            <MobileNav />

            <div class="font-bold hidden lg:flex items-center gap-x-8">
                <Dropdown />
                <a
                    href="https://2077.xyz/support"
                    target="_blank"
                    class="font-bold hover:text-greenLm dark:hover:text-green"
                    >Support us</a
                >
                <a
                    href="#subscribe"
                    class="bg-black text-white dark:bg-green dark:text-black px-8 py-2 rounded font-bold"
                >
                    Subscribe
                </a>
            </div>
            <ToggleTheme />
        </div>
    </nav>
</header>
