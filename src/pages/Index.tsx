import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import Icon from '@/components/ui/icon';
import { toast } from 'sonner';

interface Nomination {
  id: number;
  title: string;
  emoji: string;
  description: string;
  votes: number;
}

const API_URL = 'https://functions.poehali.dev/e2f0afd8-235b-4f3f-84c6-b28f4d91636b';
const VOTE_END_DATE = new Date('2025-12-31T23:59:59');

export default function Index() {
  const [nominations, setNominations] = useState<Nomination[]>([]);
  const [votedFor, setVotedFor] = useState<Set<number>>(new Set());
  const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0 });
  const [showResults, setShowResults] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNominations();
  }, []);

  useEffect(() => {
    const calculateTimeLeft = () => {
      const now = new Date().getTime();
      const end = VOTE_END_DATE.getTime();
      const difference = end - now;

      if (difference > 0) {
        setTimeLeft({
          days: Math.floor(difference / (1000 * 60 * 60 * 24)),
          hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
          minutes: Math.floor((difference / 1000 / 60) % 60),
          seconds: Math.floor((difference / 1000) % 60)
        });
      }
    };

    calculateTimeLeft();
    const timer = setInterval(calculateTimeLeft, 1000);

    return () => clearInterval(timer);
  }, []);

  const fetchNominations = async () => {
    try {
      const response = await fetch(API_URL);
      const data = await response.json();
      setNominations(data.nominations);
      setVotedFor(new Set(data.votedFor));
      setLoading(false);
    } catch (error) {
      toast.error('Ошибка загрузки данных');
      setLoading(false);
    }
  };

  const handleVote = async (id: number) => {
    if (votedFor.has(id)) {
      toast.error('Вы уже проголосовали за эту номинацию!');
      return;
    }

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nominationId: id })
      });

      const data = await response.json();

      if (response.ok) {
        setNominations(prev =>
          prev.map(nom =>
            nom.id === id ? { ...nom, votes: nom.votes + 1 } : nom
          )
        );
        setVotedFor(prev => new Set(prev).add(id));
        toast.success('Ваш голос учтён!');
      } else {
        toast.error(data.error || 'Ошибка голосования');
      }
    } catch (error) {
      toast.error('Ошибка соединения с сервером');
    }
  };

  const totalVotes = nominations.reduce((sum, nom) => sum + nom.votes, 0);
  const sortedNominations = [...nominations].sort((a, b) => b.votes - a.votes);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Icon name="Loader2" size={48} className="animate-spin text-primary mx-auto mb-4" />
          <p className="text-xl text-muted-foreground">Загрузка...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-12 max-w-7xl">
        <div className="text-center mb-16 animate-fade-in">
          <h1 className="text-6xl md:text-8xl font-bold mb-6 text-gradient">
            СЛЕЙ 2025
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-8">
            Голосование за лучших из лучших
          </p>
          
          <Card className="glass-card p-8 max-w-3xl mx-auto glow-effect mb-8">
            <div className="flex items-center justify-center gap-2 mb-4">
              <Icon name="Clock" size={24} className="text-primary" />
              <h2 className="text-2xl font-bold">До завершения голосования</h2>
            </div>
            <div className="grid grid-cols-4 gap-4 text-center">
              {[
                { label: 'Дней', value: timeLeft.days },
                { label: 'Часов', value: timeLeft.hours },
                { label: 'Минут', value: timeLeft.minutes },
                { label: 'Секунд', value: timeLeft.seconds }
              ].map((item) => (
                <div key={item.label} className="bg-muted/30 rounded-lg p-4">
                  <div className="text-4xl md:text-5xl font-bold text-gradient mb-2">
                    {item.value.toString().padStart(2, '0')}
                  </div>
                  <div className="text-sm text-muted-foreground">{item.label}</div>
                </div>
              ))}
            </div>
          </Card>

          <div className="flex gap-4 justify-center">
            <Button
              size="lg"
              variant={showResults ? 'outline' : 'default'}
              onClick={() => setShowResults(false)}
              className="text-lg"
            >
              <Icon name="Vote" size={20} className="mr-2" />
              Голосование
            </Button>
            <Button
              size="lg"
              variant={showResults ? 'default' : 'outline'}
              onClick={() => setShowResults(true)}
              className="text-lg"
            >
              <Icon name="BarChart3" size={20} className="mr-2" />
              Результаты
            </Button>
          </div>
        </div>

        {!showResults ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {nominations.map((nom, index) => (
              <Card
                key={nom.id}
                className="glass-card p-6 hover:glow-effect transition-all duration-300 hover:scale-105 animate-scale-in"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <div className="text-center mb-4">
                  <div className="text-6xl mb-4 animate-pulse-glow inline-block">
                    {nom.emoji}
                  </div>
                  <h3 className="text-2xl font-bold mb-2">{nom.title}</h3>
                  <p className="text-muted-foreground text-sm">{nom.description}</p>
                </div>
                <Button
                  onClick={() => handleVote(nom.id)}
                  disabled={votedFor.has(nom.id)}
                  className="w-full text-lg"
                  size="lg"
                >
                  {votedFor.has(nom.id) ? (
                    <>
                      <Icon name="CheckCircle" size={20} className="mr-2" />
                      Проголосовано
                    </>
                  ) : (
                    <>
                      <Icon name="ThumbsUp" size={20} className="mr-2" />
                      Голосовать
                    </>
                  )}
                </Button>
              </Card>
            ))}
          </div>
        ) : (
          <div className="space-y-6">
            <Card className="glass-card p-8 text-center mb-8">
              <h2 className="text-3xl font-bold mb-4">Текущие результаты</h2>
              <p className="text-xl text-muted-foreground">
                Всего голосов: <span className="text-primary font-bold">{totalVotes}</span>
              </p>
            </Card>

            <div className="space-y-4">
              {sortedNominations.map((nom, index) => {
                const percentage = totalVotes > 0 ? (nom.votes / totalVotes) * 100 : 0;
                const isTop3 = index < 3;
                
                return (
                  <Card
                    key={nom.id}
                    className={`glass-card p-6 ${isTop3 ? 'glow-effect' : ''} animate-fade-in`}
                    style={{ animationDelay: `${index * 0.05}s` }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="text-4xl font-bold text-muted-foreground min-w-[3rem]">
                        #{index + 1}
                      </div>
                      <div className="text-5xl">{nom.emoji}</div>
                      <div className="flex-1">
                        <h3 className="text-2xl font-bold mb-1">{nom.title}</h3>
                        <p className="text-sm text-muted-foreground">{nom.description}</p>
                      </div>
                      <div className="text-right min-w-[5rem]">
                        <div className="text-3xl font-bold text-gradient">{nom.votes}</div>
                        <div className="text-sm text-muted-foreground">голосов</div>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Процент голосов</span>
                        <span className="font-bold">{percentage.toFixed(1)}%</span>
                      </div>
                      <Progress value={percentage} className="h-3" />
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
