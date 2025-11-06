// Reference datasets sourced from CoinGecko public documentation
// https://docs.coingecko.com/reference/introduction

export const SOLANA_REALTIME_PRICE = {
  solana: {
    usd: 161.01,
    gbp: 120.67,
    aud: 250.77,
    cad: 224.67,
    eur: 143.49
  }
}

export const SOLANA_HISTORICAL_PRICES = {
  prices: [
    [1746921600000, 177.3428319704922],
    [1747008000000, 172.85779222329435],
    [1747094400000, 174.41950190990173],
    [1747180800000, 184.05379777179434],
    [1747267200000, 176.45507175799847],
    [1747326501000, 171.87940633690812]
  ]
}

export const SOLANA_METADATA = {
  id: 'solana',
  symbol: 'sol',
  name: 'Solana',
  web_slug: 'solana',
  image: {
    thumb: 'https://coin-images.coingecko.com/coins/images/4128/thumb/solana.png?1718769756',
    small: 'https://coin-images.coingecko.com/coins/images/4128/small/solana.png?1718769756',
    large: 'https://coin-images.coingecko.com/coins/images/4128/large/solana.png?1718769756'
  },
  asset_platform_id: null,
  platforms: {
    '': ''
  },
  detail_platforms: {
    '': {
      decimal_place: null,
      contract_address: ''
    }
  },
  block_time_in_minutes: 0,
  hashing_algorithm: null,
  categories: [
    'Smart Contract Platform',
    'Solana Ecosystem',
    'Layer 1 (L1)',
    'Alleged SEC Securities',
    'FTX Holdings',
    'Multicoin Capital Portfolio',
    'Proof of Stake (PoS)',
    'Alameda Research Portfolio',
    'Andreessen Horowitz (a16z) Portfolio',
    'GMCI Layer 1 Index',
    'GMCI 30 Index',
    'Delphi Ventures Portfolio',
    'GMCI Index',
    'Polychain Capital Portfolio',
    'Made in USA',
    'Coinbase 50 Index'
  ],
  preview_listing: false,
  public_notice: null,
  additional_notices: [] as string[],
  description: {
    en: 'Solana is a highly functional open source project that banks on blockchain technology\'s permissionless nature to provide decentralized finance (DeFi) solutions. It is a layer 1 network that offers fast speeds and affordable costs. While the idea and initial work on the project began in 2017, Solana was officially launched in March 2020 by the Solana Foundation with headquarters in Geneva, Switzerland.'
  },
  links: {
    homepage: ['https://solana.com/'],
    whitepaper: '',
    blockchain_site: [
      'https://solscan.io/',
      'https://platform.arkhamintelligence.com/explorer/token/solana',
      'https://xray.helius.xyz/',
      'https://solana.fm/',
      'https://solanabeach.io/',
      'https://www.oklink.com/sol',
      'https://explorer.solana.com/'
    ],
    official_forum_url: [] as string[],
    chat_url: [] as string[],
    announcement_url: [] as string[],
    snapshot_url: null,
    twitter_screen_name: 'solana',
    facebook_username: '',
    bitcointalk_thread_identifier: null,
    telegram_channel_identifier: 'solana',
    subreddit_url: 'https://www.reddit.com/r/solana',
    repos_url: {
      github: ['https://github.com/solana-labs/solana'],
      bitbucket: [] as string[]
    }
  },
  country_origin: '',
  genesis_date: null,
  sentiment_votes_up_percentage: 77.45,
  sentiment_votes_down_percentage: 22.55,
  ico_data: {
    ico_start_date: null,
    ico_end_date: null,
    short_desc: 'High-Performance Blockchain',
    description: null as string | null,
    links: {} as Record<string, unknown>,
    softcap_currency: '',
    hardcap_currency: '',
    total_raised_currency: '',
    softcap_amount: null as number | null,
    hardcap_amount: null as number | null,
    total_raised: null as number | null,
    quote_pre_sale_currency: '',
    base_pre_sale_amount: null as number | null,
    quote_pre_sale_amount: null as number | null,
    quote_public_sale_currency: '',
    base_public_sale_amount: 0,
    quote_public_sale_amount: 0,
    accepting_currencies: '',
    country_origin: '',
    pre_sale_start_date: null,
    pre_sale_end_date: null,
    whitelist_url: 'https://solana.com/presale/',
    whitelist_start_date: null,
    whitelist_end_date: null,
    bounty_detail_url: '',
    amount_for_sale: null as number | null,
    kyc_required: true,
    whitelist_available: true,
    pre_sale_available: null as boolean | null,
    pre_sale_ended: false
  },
  watchlist_portfolio_users: 1080399,
  market_cap_rank: 6,
  community_data: {
    facebook_likes: null as number | null,
    twitter_followers: 3386832,
    reddit_average_posts_48h: 0,
    reddit_average_comments_48h: 0,
    reddit_subscribers: 0,
    reddit_accounts_active_48h: 0,
    telegram_channel_user_count: 73213
  },
  developer_data: {
    forks: 3516,
    stars: 11071,
    subscribers: 276,
    total_issues: 5177,
    closed_issues: 4611,
    pull_requests_merged: 23614,
    pull_request_contributors: 411,
    code_additions_deletions_4_weeks: {
      additions: 10193,
      deletions: -5277
    },
    commit_count_4_weeks: 171,
    last_4_weeks_commit_activity_series: [] as number[]
  },
  status_updates: [] as string[],
  last_updated: '2025-05-15T16:37:07.656Z'
}
