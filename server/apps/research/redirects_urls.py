from django.urls import path
from .views import LoggingRedirectView

urlpatterns = [
    # Existing redirects
    path('api/articles/block-stm-vs-sealevel-1/', 
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/block-stm_vs_sealevel/', permanent=True)),
    path('api/articles/eips-for-nerds-8-eip-7685/', 
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/EIP-7685-General-Purpose-Execution-Requests/', permanent=True)),
    path('api/articles/research/eips-for-nerds-8-eip-7685/', 
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/EIP-7685-General-Purpose-Execution-Requests/', permanent=True)),
    path('api/articles/charting-ethereums-account-abstraction-roadmap-1/', 
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/charting-ethereums-account-abstraction-roadmap-i-eip-3074-eip-7702/', permanent=True)),

    # New redirects for Substack articles
    path('p/eip-7503-zero-knowledge-wormholes/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/eip-7503-zero-knowledge-wormholes-for-private-ethereum-transactions', permanent=True)),
    path('p/eip-6110-supply-validator-deposits-onchain/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/eip-6110-fixing-beacon-chain-tech-debt', permanent=True)),
    path('p/eip-7251-increase-max-effective-balance/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/eip-7251-raising-maximum-effective-balance-for-validators', permanent=True)),
    path('p/a-guide-to-erc-7512-on-chain-representation/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/erc-7512-bolstering-smart-contract-security-with-on-chain-audits', permanent=True)),
    path('p/verkle-trees-for-the-rest-of-us-part-1/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/verkle-trees', permanent=True)),
    path('p/data-availability-in-ethereum-rollups/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/data-availability-or-how-rollups-learned-to-stop-worrying-and-love-ethereum', permanent=True)),
    path('p/eip-7002-execution-layer-exits/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/eip-7002-unpacking-improvements-to-staking-ux-post-merge', permanent=True)),
    path('p/eips-for-nerds-6-erc-5564-and-erc/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/erc-5564-erc-6358-unlocking-privacy-on-ethereum-with-stealth-addresses', permanent=True)),
    path('p/eip-7657-sync-committee-slashings/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/eip-7657-securing-ethereums-sync-committee', permanent=True)),
    path('p/understanding-blockchain-governance/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/understanding-blockchain-governance', permanent=True)),

    # Redirects for URLs no longer on the website to the homepage
    path('p/monthly-stablecoin-report-1/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/', permanent=True)),
    path('p/weekly-stablecoin-report-5/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/', permanent=True)),
    path('p/weekly-stablecoin-report-4/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/', permanent=True)),

    path('s/stablecoin-reports/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/', permanent=True)),
    path('s/state-of-ethereum-governance/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/', permanent=True)),
    path('about/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/', permanent=True)),
    path('archive/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/', permanent=True)),
    path('p/announcing-ethereum-2077-newsletter/',
         LoggingRedirectView.as_view(url='https://www.research.2077.xyz/', permanent=True)),
]