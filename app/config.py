import os

# Environment variables
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not DISCORD_WEBHOOK or not OPENAI_API_KEY:
    raise ValueError("DISCORD_WEBHOOK and OPENAI_API_KEY must be set as environment variables.")

# Define channel-prompt pairs
CHANNELS = {
    "UCFQsi7WaF5X41tcuOryDk8w": "请提取视频中的精华，以及视频对市场低点的预判和买入时间。要求说得简单易懂。不要使用过多的 markdown 格式，因为我会把这段原文贴到 Discord。只输出以下内容，别加多余的话。\n这些信息不要遗漏，没有的话不需要提取：\n市场是否有涨幅？原因是什么？市场还安全吗？指数关键点位？热门股票关键价位？买入时机建议？当前策略？哪些股票值得买入？为什么？这些股票的估值是什么？\n因为特朗普说要暂停对很多国家加征关税90天，但对中国的关税反而提高到125%。\n",
    "UCFhJ8ZFg9W4kLwFTBBNIjOw": "请提取视频中的精华，以及视频对市场低点的预判和买入时间。要求说得简单易懂。不要使用过多的 markdown 格式，因为我会把这段原文贴到 Discord。只输出以下内容，别加多余的话。\n这些信息不要遗漏，没有的话不需要提取：\n市场是否有涨幅？原因是什么？市场还安全吗？指数关键点位？热门股票关键价位？买入时机建议？当前策略？哪些股票值得买入？为什么？这些股票的估值是什么？\n因为特朗普说要暂停对很多国家加征关税90天，但对中国的关税反而提高到125%。\n",
    "UCjrP2TtSTifuRJ76hW2IW1A": "请提取视频中的精华，以及视频对市场低点的预判和买入时间。要求说得简单易懂。不要使用过多的 markdown 格式，因为我会把这段原文贴到 Discord。只输出以下内容，别加多余的话。\n这些信息不要遗漏，没有的话不需要提取：\n市场是否有涨幅？原因是什么？市场还安全吗？指数关键点位？热门股票关键价位？买入时机建议？当前策略？哪些股票值得买入？为什么？这些股票的估值是什么？\n因为特朗普说要暂停对很多国家加征关税90天，但对中国的关税反而提高到125%。\n"
}