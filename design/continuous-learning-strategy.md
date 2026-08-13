# Continuous Learning and Multiuser Strategy

## Product principle

The product should encourage continuous learning through visible progress, achievable daily practice, useful content, and supportive friendships. It should not depend on pressure, punishment, or competition.

The central promise is:

> Every session helps the learner understand, speak, and write a little more Spanish, while the next session automatically adapts to what they need.

## The personal learning loop

Each learner receives a daily path lasting approximately 10–15 minutes:

1. Watch a short segment from a local or reviewed online video.
2. Listen to and understand important phrases.
3. Repeat selected lines and receive pronunciation feedback.
4. Complete vocabulary, grammar, writing, and listening exercises.
5. Review mistakes with short explanations.
6. Receive the next lesson based on their performance and interests.

The system should track pronunciation, vocabulary, grammar, writing, listening comprehension, and fluency separately. A learner may advance faster in one skill while receiving additional support in another.

## Features that encourage consistency

### Short, achievable sessions

The normal daily session should fit into 10–15 minutes. Learners can continue when motivated, but completing the essential session should always feel realistic.

### Meaningful progress

Show specific accomplishments instead of only points. Examples include:

- “You understood a complete A2 conversation.”
- “You learned 18 useful words this week.”
- “Your pronunciation of the soft ‘d’ improved.”
- “You can now write about weekend plans.”

### Flexible streaks

Reward consistency while allowing one or two recovery days. Missing a day must not erase all previous progress or make the learner feel that they have failed.

### Weekly goals

Let learners choose goals that match their schedule, such as:

- Complete three lessons.
- Practise listening for 30 minutes.
- Speak 20 Spanish sentences.
- Write two short responses.

### Spaced review

Automatically bring back vocabulary, grammar, and pronunciation patterns shortly before the learner is likely to forget them. Reviews should be short and mixed into new lessons.

### Personal interests

Recommend lessons based on interests such as travel, food, daily life, work, stories, culture, and conversation. Content should also match the learner’s current level.

### Balanced difficulty

Most exercises should feel achievable, with a smaller number providing a useful challenge. If a learner struggles, the system should offer a simpler explanation or practice activity without presenting this as failure.

## Multiuser experience for friends

Each person should have an individual account, private learning profile, adaptive level, history, and goals. Friends can join small private groups.

Useful social features include:

- Private friend groups rather than a large public network.
- Weekly group activity with detailed personal scores private by default.
- Cooperative goals such as completing 20 listening activities together.
- Simple encouragement messages such as “¡Buen trabajo!”.
- Optional conversation partners matched by level and availability.
- Shared weekly discussion prompts based on lesson videos.
- Group celebrations for consistency and participation, not language ability.

The product should avoid public mistakes, public skill rankings, and leaderboards that make beginners feel inferior.

## Suggested weekly rhythm

| Day | Main activity |
| --- | --- |
| Monday | New video lesson |
| Tuesday | Vocabulary and grammar review |
| Wednesday | Pronunciation practice |
| Thursday | Short writing prompt |
| Friday | Listening and conversation quiz |
| Weekend | Optional friend conversation and weekly recap |

The schedule should remain flexible. The adaptive system can rearrange activities when a learner has limited time or needs additional review.

## Weekly recap

The weekly recap is one of the most important retention features. It should connect time spent with real language improvement.

Example:

> This week you studied for 42 minutes, learned 18 words, and improved your pronunciation of the soft “d”. Next week, we’ll practise future plans through travel conversations.

It should contain:

- Time spent and lessons completed.
- Newly learned and reviewed vocabulary.
- Improvement in each language skill.
- One meaningful achievement.
- One friendly recommendation for the next week.
- Optional group progress and encouragement.

## Content growth

The lesson library can grow from three sources:

1. Videos automatically discovered in `/srv/files/ytwatcher/Espanol/`.
2. Spanish-learning files from `/home/justin/Projects/Espanol/Vitamina/`.
3. Suitable online materials selected for learning value.

The Español and Vitamina directories should both be watched continuously. Newly added files should enter the same preparation pipeline automatically, while retaining their source-library label so they can be filtered, audited, or reprocessed later.

The Vitamina collection currently covers A1, A2, B1, B2, and C1. Its different document types should have distinct roles:

- `Libro del alumno`: lesson structure, explanations, vocabulary, examples, and progression.
- `Cuaderno de ejercicios`: inspiration for practice and assessment formats.
- `Soluciones` or `Solucionario`: validation of generated answers.
- `Guía didáctica`: teaching objectives, sequencing, and pedagogical guidance.

OCR versions should be preferred for text extraction when their quality is adequate. Scanned editions may require OCR and page-quality checks before ingestion. Source page, book, edition, and CEFR level should remain attached to every derived lesson item.

Before becoming a lesson, content should be transcribed, divided into useful segments, classified by CEFR level and topic, and reviewed for audio quality and correctness. The system can then generate vocabulary, grammar, writing, listening, and pronunciation activities from it.

Every lesson should retain its source label: `Español`, `Vitamina`, or `Online reviewed`. Online content should be labelled as reviewed. Copyright, licensing, attribution, and source availability must be checked before it is redistributed or embedded.

## What to avoid

- Aggressive or public leaderboards.
- Losing all streak progress after one missed day.
- Excessive notifications or guilt-based reminders.
- Points and badges disconnected from genuine learning.
- Long compulsory lessons.
- Repeating exercises without explaining why.
- Showing a learner’s mistakes or detailed scores to friends by default.
- Advancing every skill together when the learner has uneven strengths.

## Success criteria

The design is successful when learners:

- Return several times each week without feeling pressured.
- Can explain what they have improved.
- Receive lessons appropriate to their current ability.
- Review weak areas before forgetting them.
- Feel supported by friends without being judged against them.
- Gradually become more capable in real Spanish conversations.
