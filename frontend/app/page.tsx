export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <h1 className="text-4xl font-bold mb-4">AreaYield OS</h1>
      <p className="text-xl text-muted-foreground mb-8 text-center max-w-2xl">
        短期賃貸（民泊）投資の可否判定を、収益性・許認可実現性・規制リスクの3軸で評価
      </p>
      <div className="flex gap-4">
        <button className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
          分析を開始
        </button>
        <button className="px-6 py-3 border border-input rounded-lg hover:bg-accent">
          詳細を見る
        </button>
      </div>
    </div>
  )
}

