<div class="fixed top-0 left-0">
    <div class="w-screen m-auto">
        <div class="bg-[#cccccc] w-full h-[5px]">
            <div class="progress-bar-value bg-black w-full h-full bg-black" />
        </div>
    </div>
</div>

<style scoped>
    .progress-bar-value {
        animation: indeterminateAnimation 1s infinite linear;
        transform-origin: 0% 50%;
    }

    @keyframes indeterminateAnimation {
        0% {
            transform: translateX(0) scaleX(0);
        }
        40% {
            transform: translateX(0) scaleX(0.4);
        }
        100% {
            transform: translateX(100%) scaleX(0.5);
        }
    }
</style>
