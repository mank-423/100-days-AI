from .agent import run_agent, write_file

write_file('notes.txt', 'Mitosis makes two identical cells. Meiosis makes four different cells with half the chromosomes. Meiosis involves crossing over.')

result = run_agent(goal='Read notes.txt, then write summary.md with 3 bullet points, then tell me you are done.', system='You are Pagewise. Work only inside the workspace. Be efficient.',)

print(result)
