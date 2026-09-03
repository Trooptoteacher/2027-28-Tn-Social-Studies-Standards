# Review worksheet — AI first pass

**Nothing here is approved.** Every row is a recommendation with its evidence and what it could not check. `aiReview` counts toward no gate and lets nothing ship — your decision is still the only one that settles anything.

- **0** recommended for a fast confirm
- **30** with a bounded fix drafted (not applied)
- **10** that need your judgement

Record decisions in `reviewed/ai-review.json` (`humanVerdict` per row), then apply approvals through `tools/apply_review.py` as usual.

## Fix drafted — read the draft, then decide

### `US.01-X020` · US.04 · key-contradiction

**The key is D. Its explanation says: "Option D is incorrect because this ideology directly shaped federal land and military policy throughout the 19th century." — deleting it leaves too little behind. What should this rationale say instead?**

> How did the ideology of Manifest Destiny shape U.S. policy toward American Indian peoples in the late 19th century?

*Checked:*
- key is 'D'; key text is 'It provided ideological justification for westward territorial expansion and the'
- the sentence is a distractor rationale left pointing at the old letter
- deletion leaves only 1 sentence(s) — not a finished argument

*Could NOT check:*
- whether the key itself is correct — a claim about history
- what the replacement should assert

*Draft (not applied):*
```json
{
  "action": "rewrite",
  "remove": "Option D is incorrect because this ideology directly shaped federal land and military policy throughout the 19th century.",
  "wouldLeave": "Manifest Destiny — the belief that American expansion across the continent was divinely ordained and inevitable — justified the removal of American Indians from their lands, broken treaties, and the reservation system as necessary steps in a foreordained national progress."
}
```

### `US.01-X021` · US.04 · key-contradiction

**The key is A. Its explanation says: "Option A is incorrect because the Great Plains suffer from insufficient rainfall and drought, not flooding." — deleting it leaves too little behind. What should this rationale say instead?**

> Which of the following best explains why farming on the Great Plains was especially difficult for homesteaders in the late 19th century?

*Checked:*
- key is 'A'; key text is 'Insufficient timber for construction, scarce water, periodic droughts, and hard '
- the sentence is a distractor rationale left pointing at the old letter
- deletion leaves only 1 sentence(s) — not a finished argument

*Could NOT check:*
- whether the key itself is correct — a claim about history
- what the replacement should assert

*Draft (not applied):*
```json
{
  "action": "rewrite",
  "remove": "Option A is incorrect because the Great Plains suffer from insufficient rainfall and drought, not flooding.",
  "wouldLeave": "Great Plains homesteaders faced a harsh semi-arid environment — treeless, with hard sod and unreliable rainfall — that rendered Eastern farming methods useless and required technological adaptations like steel-tipped plows, windmills, and dry-farming techniques."
}
```

### `q-new-us09-dok1-carnegie` · US.09 · key-contradiction

**The key is D. Delete this intruding sentence? Read the AFTER text — if it still says why D is right, this is a yes.**

> Andrew Carnegie built his industrial fortune primarily in which industry?

*Checked:*
- key is 'D'; key text is 'Steel production and manufacturing for construction purposes'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "Choice D is wrong if it names oil, because that was Rockefeller’s field, not Carnegie’s.",
  "before": "Andrew Carnegie made his fortune in steel by using the Bessemer process and controlling production from raw materials to shipping. Choice D is wrong if it names oil, because that was Rockefeller’s field, not Carnegie’s. Carnegie’s company became a classic example of large-scale industrial capitalism.",
  "after": "Andrew Carnegie made his fortune in steel by using the Bessemer process and controlling production from raw materials to shipping. Carnegie’s company became a classic example of large-scale industrial capitalism."
}
```

### `q-new-us09-dok2-rockefeller` · US.09 · key-contradiction

**The key is B. Delete this intruding sentence? Read the AFTER text — if it still says why B is right, this is a yes.**

> John D. Rockefeller's Standard Oil Company was an example of —

*Checked:*
- key is 'B'; key text is 'A monopoly that controlled oil refining and distribution'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup.",
  "before": "Ida Tarbell documented how Standard Oil used secret rebates and other unfair tactics to crush competitors, helping build public support for action against Rockefeller’s monopoly. Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup. Her investigation became one of the best-known examples of muckraking journalism shaping reform.",
  "after": "Ida Tarbell documented how Standard Oil used secret rebates and other unfair tactics to crush competitors, helping build public support for action against Rockefeller’s monopoly. Her 
```

### `q-tcap-us09-urbanization-1` · US.15 · key-contradiction

**The key is D. Delete this intruding sentence? Read the AFTER text — if it still says why D is right, this is a yes.**

> Which city became a major center for steel production due to its location near coal and iron ore deposits?

*Checked:*
- key is 'D'; key text is 'Pittsburgh'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "Choice D is wrong if it names oil, because that was Rockefeller’s field, not Carnegie’s.",
  "before": "Andrew Carnegie made his fortune in steel by using the Bessemer process and controlling production from raw materials to shipping. Choice D is wrong if it names oil, because that was Rockefeller’s field, not Carnegie’s. Carnegie’s company became a classic example of large-scale industrial capitalism, and this question specifically highlights city became major center steel production.",
  "after": "Andrew Carnegie made his fortune in steel by using the Bessemer process and controlling production from raw materials to shipping. Carnegie’s company became a classic example of large-scale industrial capitalism, and this question specifically highlights city became major center steel production."
}
```

### `q-us09-dok2-6` · US.09 · key-contradiction

**The key is B. Delete this intruding sentence? Read the AFTER text — if it still says why B is right, this is a yes.**

> What business practice did John D. Rockefeller primarily use to build Standard Oil?

*Checked:*
- key is 'B'; key text is 'Horizontal integration - buying out competing oil refineries'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup.",
  "before": "Ida Tarbell documented how Standard Oil used secret rebates and other unfair tactics to crush competitors, helping build public support for action against Rockefeller’s monopoly. Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup. Her investigation became one of the best-known examples of muckraking journalism shaping reform, with the clue centered on business practice John D Rockefeller use.",
  "after": "Ida Tarbell documented how Standard Oil used secret rebates and other unfair tactics to crush competitors, helping 
```

### `q-us14-dok1-2-u2` · US.16 · key-contradiction

**The key is B. Delete this intruding sentence? Read the AFTER text — if it still says why B is right, this is a yes.**

> What did Ida Tarbell's investigative reporting expose?

*Checked:*
- key is 'B'; key text is 'The monopolistic practices of Standard Oil Company'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup.",
  "before": "Ida Tarbell documented how Standard Oil used secret rebates and other unfair tactics to crush competitors, helping build public support for action against Rockefeller’s monopoly. Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup. Her investigation became one of the best-known examples of muckraking journalism shaping reform, which is especially clear in the item's focus on ida Tarbell s investigative reporting expose.",
  "after": "Ida Tarbell documented how Standard Oil used secret rebates and other unfair tactics to 
```

### `q-us14-dok1-tarbell` · US.16 · key-contradiction

**The key is B. Delete this intruding sentence? Read the AFTER text — if it still says why B is right, this is a yes.**

> What company did Ida Tarbell expose in her investigative journalism?

*Checked:*
- key is 'B'; key text is 'Standard Oil'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup.",
  "before": "Ida Tarbell documented how Standard Oil used secret rebates and other unfair tactics to crush competitors, helping build public support for action against Rockefeller’s monopoly. Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup. Her investigation became one of the best-known examples of muckraking journalism shaping reform, and here the emphasis is on company Ida Tarbell expose her investigative.",
  "after": "Ida Tarbell documented how Standard Oil used secret rebates and other unfair tactics to crush competitors, he
```

### `q-us73-add-2` · US.66 · key-contradiction

**The key is D. Delete this intruding sentence? Read the AFTER text — if it still says why D is right, this is a yes.**

> What medical advance during the 1950s dramatically improved public health?

*Checked:*
- key is 'D'; key text is "Jonas Salk's polio vaccine, which nearly eliminated a feared childhood disease"
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "B is wrong because highways were a transportation change, not a medical advance, and D is wrong because it describes a broad result rather than the specific breakthrough.",
  "before": "Jonas Salk's polio vaccine, introduced in 1955, sharply reduced a disease that had terrified families and paralyzed thousands of children. B is wrong because highways were a transportation change, not a medical advance, and D is wrong because it describes a broad result rather than the specific breakthrough. The vaccine strengthened public faith in science and public-health campaigns during the postwar era.",
  "after": "Jonas Salk's polio vaccine, introduced in 1955, sharply reduced a disease that had terrified families and paralyzed thousands of children. The vaccine strengthened public faith in science and public-health campaigns during the postwar era.
```

### `q-us73-add-3` · US.66 · key-contradiction

**The key is B. Delete this intruding sentence? Read the AFTER text — if it still says why B is right, this is a yes.**

> Which domestic objective helped Eisenhower justify the Interstate Highway System?

*Checked:*
- key is 'B'; key text is 'Improving civilian transportation while supporting national defense logistics'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "B is wrong because the polio vaccine had nothing to do with highway policy.",
  "before": "Eisenhower justified the Interstate Highway System partly as a way to improve civilian travel while also moving troops and supplies quickly in an emergency. B is wrong because the polio vaccine had nothing to do with highway policy. Cold War defense concerns helped win support for a major domestic building project.",
  "after": "Eisenhower justified the Interstate Highway System partly as a way to improve civilian travel while also moving troops and supplies quickly in an emergency. Cold War defense concerns helped win support for a major domestic building project."
}
```

### `q-us75-add-3` · US.67 · key-contradiction

**The key is D. Delete this intruding sentence? Read the AFTER text — if it still says why D is right, this is a yes.**

> How did television contribute to a more national popular culture in the 1950s?

*Checked:*
- key is 'D'; key text is 'Families across regions watched the same news, sports, and entertainment program'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "D is wrong because advertising shaped buying habits more than shared culture, and C is wrong because it focuses on campaigns.",
  "before": "Television helped create a national popular culture because families in different regions watched the same news, sports, and entertainment shows. D is wrong because advertising shaped buying habits more than shared culture, and C is wrong because it focuses on campaigns. TV made Americans more likely to share common celebrities, programs, and public moments.",
  "after": "Television helped create a national popular culture because families in different regions watched the same news, sports, and entertainment shows. TV made Americans more likely to share common celebrities, programs, and public moments."
}
```

### `q-us76-add-5` · US.68 · key-contradiction

**The key is B. Delete this intruding sentence? Read the AFTER text — if it still says why B is right, this is a yes.**

> How did Tennessee recording centers help shape youth culture in the 1950s?

*Checked:*
- key is 'B'; key text is 'Studios in Memphis and Nashville popularized crossover sounds that reached natio'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 3 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "B is wrong because B.B.",
  "before": "Recording centers in Memphis and Nashville helped shape youth culture by spreading crossover music that appealed to teenagers nationwide. B is wrong because B.B. King was important but the question asks about studios and music centers, not one artist. Tennessee helped define what many young Americans listened to in the 1950s.",
  "after": "Recording centers in Memphis and Nashville helped shape youth culture by spreading crossover music that appealed to teenagers nationwide. King was important but the question asks about studios and music centers, not one artist. Tennessee helped define what many young Americans listened to in the 1950s."
}
```

### `q-us77-add-2` · US.72 · key-contradiction

**The key is D. Delete this intruding sentence? Read the AFTER text — if it still says why D is right, this is a yes.**

> How did Kennedy's assassination in 1963 affect American society?

*Checked:*
- key is 'D'; key text is 'It traumatized the nation and created sympathy that helped pass his legislative '
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "D is wrong because it describes the New Frontier itself, not the effect of Kennedy's death.",
  "before": "Kennedy's assassination shocked the nation and created a wave of sympathy that helped Lyndon Johnson push parts of Kennedy's agenda through Congress. D is wrong because it describes the New Frontier itself, not the effect of Kennedy's death. The tragedy became a turning point in American politics and public memory.",
  "after": "Kennedy's assassination shocked the nation and created a wave of sympathy that helped Lyndon Johnson push parts of Kennedy's agenda through Congress. The tragedy became a turning point in American politics and public memory."
}
```

### `q-us77-add-5` · US.72 · key-contradiction

**The key is B. Delete this intruding sentence? Read the AFTER text — if it still says why B is right, this is a yes.**

> How did New Frontier proposals influence later domestic policy even when not fully enacted under Kennedy?

*Checked:*
- key is 'B'; key text is 'They provided legislative foundations that Johnson advanced through Great Societ'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "B is wrong because the Peace Corps was only one program, not the broader legacy.",
  "before": "Even when Kennedy did not get all of his proposals passed, the New Frontier shaped later laws by giving Johnson ideas and political groundwork to build on. B is wrong because the Peace Corps was only one program, not the broader legacy. This continuity shows how presidential agendas can matter even beyond one administration.",
  "after": "Even when Kennedy did not get all of his proposals passed, the New Frontier shaped later laws by giving Johnson ideas and political groundwork to build on. This continuity shows how presidential agendas can matter even beyond one administration."
}
```

### `q-us86-add-1` · US.84 · key-contradiction

**The key is A. Delete this intruding sentence? Read the AFTER text — if it still says why A is right, this is a yes.**

> What was the Watergate scandal?

*Checked:*
- key is 'A'; key text is "A break-in at Democratic headquarters and Nixon's cover-up that led to his resig"
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "A is incorrect because that refers to Watergate rather than the concept asked about here; D is incorrect because it names a different institution or power than the one the item asks about.",
  "before": "Watergate began with a break-in at Democratic National Committee headquarters and grew into a scandal because Nixon and his aides tried to cover it up. A is incorrect because that refers to Watergate rather than the concept asked about here; D is incorrect because it names a different institution or power than the one the item asks about. It also shows why constitutional checks matter when presidents try to expand their power.",
  "after": "Watergate began with a break-in at Democratic National Committee headquarters and grew into a scandal because Nixon and his aides tried to cover it up. It also shows why constitutional checks matter wh
```

### `q-us93-3` · US.92 · key-contradiction

**The key is C. Delete this intruding sentence? Read the AFTER text — if it still says why C is right, this is a yes.**

> What barrier did Nancy Pelosi break in American political history in 2007?

*Checked:*
- key is 'C'; key text is 'She became the first woman to serve as Speaker of the House'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "B is incorrect because it identifies a different historic barrier-breaking achievement; C is incorrect because it identifies a different historic barrier-breaking achievement.",
  "before": "Nancy Pelosi made history in 2007 by becoming the first woman to serve as Speaker of the House. B is incorrect because it identifies a different historic barrier-breaking achievement; C is incorrect because it identifies a different historic barrier-breaking achievement. It also helps explain how symbolic breakthroughs can change who Americans imagine in positions of power.",
  "after": "Nancy Pelosi made history in 2007 by becoming the first woman to serve as Speaker of the House. It also helps explain how symbolic breakthroughs can change who Americans imagine in positions of power."
}
```

### `q-us93-add-3` · US.92 · key-contradiction

**The key is C. Delete this intruding sentence? Read the AFTER text — if it still says why C is right, this is a yes.**

> Who was Nancy Pelosi and what was historic about her role?

*Checked:*
- key is 'C'; key text is 'She became the first woman to serve as Speaker of the House in 2007'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "B is incorrect because it identifies a different historic barrier-breaking achievement; C is incorrect because it identifies a different historic barrier-breaking achievement.",
  "before": "Nancy Pelosi made history in 2007 by becoming the first woman to serve as Speaker of the House. B is incorrect because it identifies a different historic barrier-breaking achievement; C is incorrect because it identifies a different historic barrier-breaking achievement. The topic reflects a broader expansion of representation in American public life, even as barriers did not disappear overnight.",
  "after": "Nancy Pelosi made history in 2007 by becoming the first woman to serve as Speaker of the House. The topic reflects a broader expansion of representation in American public life, even as barriers did not disappear overnight."
}
```

### `us-09-x012` · US.16 · key-contradiction

**The key is B. Delete this intruding sentence? Read the AFTER text — if it still says why B is right, this is a yes.**

> Ida Tarbell's investigation of Standard Oil (1904) was significant because it —

*Checked:*
- key is 'B'; key text is 'Documented through meticulous research how Rockefeller had used secret railroad '
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup.",
  "before": "Ida Tarbell documented how Standard Oil used secret rebates and other unfair tactics to crush competitors, helping build public support for action against Rockefeller’s monopoly. Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup. Her investigation became one of the best-known examples of muckraking journalism shaping reform, with this version stressing ida Tarbell s investigation Standard Oil.",
  "after": "Ida Tarbell documented how Standard Oil used secret rebates and other unfair tactics to crush competitors, helpin
```

### `us-09-x025` · US.16 · key-contradiction

**The key is B. Delete this intruding sentence? Read the AFTER text — if it still says why B is right, this is a yes.**

> Ida Tarbell's investigation of Standard Oil relied primarily on —

*Checked:*
- key is 'B'; key text is 'Public records, court documents, and interviews that Standard Oil believed were '
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup.",
  "before": "Ida Tarbell documented how Standard Oil used secret rebates and other unfair tactics to crush competitors, helping build public support for action against Rockefeller’s monopoly. Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup. Her investigation became one of the best-known examples of muckraking journalism shaping reform, and this question narrows that idea to ida Tarbell s investigation Standard Oil.",
  "after": "Ida Tarbell documented how Standard Oil used secret rebates and other unfair tactics to crush competit
```

### `us-46-x022` · US.59 · key-contradiction

**The key is C. Delete this intruding sentence? Read the AFTER text — if it still says why C is right, this is a yes.**

> NATO (1949) was significant because it was —

*Checked:*
- key is 'C'; key text is 'The first peacetime military alliance in American history, entangling the U.S. i'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 3 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "C is incorrect because it describes a different program, event, or idea than this Cold War development.",
  "before": "Both A and C correctly describe NATO's significance. The alliance tied the United States permanently to Western Europe's defense during the Cold War. C is incorrect because it describes a different program, event, or idea than this Cold War development. It shaped the early Cold War and the postwar order the United States helped build after 1945.",
  "after": "Both A and C correctly describe NATO's significance. The alliance tied the United States permanently to Western Europe's defense during the Cold War. It shaped the early Cold War and the postwar order the United States helped build after 1945."
}
```

### `us-46-x027` · US.48 · key-contradiction

**The key is A. Delete this intruding sentence? Read the AFTER text — if it still says why A is right, this is a yes.**

> MacArthur's dismissal by Truman in April 1951 was significant constitutionally because it affirmed —

*Checked:*
- key is 'A'; key text is 'The principle that generals could not advocate for different policies publicly w'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 3 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "A is incorrect because it describes a different program, event, or idea than the topic in the question.",
  "before": "Both A and C reflect the constitutional principles at stake in MacArthur's dismissal. The war showed how Cold War tensions could turn into hot wars fought in divided countries. A is incorrect because it describes a different program, event, or idea than the topic in the question. It shaped the early Cold War and the postwar order the United States helped build after 1945.",
  "after": "Both A and C reflect the constitutional principles at stake in MacArthur's dismissal. The war showed how Cold War tensions could turn into hot wars fought in divided countries. It shaped the early Cold War and the postwar order the United States helped build after 1945."
}
```

### `us-54-x026` · US.54 · key-contradiction

**The key is C. Delete this intruding sentence? Read the AFTER text — if it still says why C is right, this is a yes.**

> The Albany Movement (1961-62) was considered a tactical failure for the Civil Rights Movement because —

*Checked:*
- key is 'C'; key text is 'The Kennedy administration refused to intervene, leaving protesters without fede'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "C is incorrect because it describes a different program, event, or idea than this civil rights development.",
  "before": "Both A and C contributed to the Albany Movement's failure. C is incorrect because it describes a different program, event, or idea than this civil rights development. It connects wartime change to the longer struggle for civil rights and equal treatment.",
  "after": "Both A and C contributed to the Albany Movement's failure. It connects wartime change to the longer struggle for civil rights and equal treatment."
}
```

### `us-56-x024` · US.76 · key-contradiction

**The key is B. Delete this intruding sentence? Read the AFTER text — if it still says why B is right, this is a yes.**

> The assassination of Martin Luther King Jr. (April 4, 1968) triggered —

*Checked:*
- key is 'B'; key text is 'Congressional passage of the Civil Rights Act of 1968 (Fair Housing Act) within '
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "B is incorrect because it describes a different program, event, or idea than this civil rights development.",
  "before": "Both A and B were immediate consequences of King's assassination. B is incorrect because it describes a different program, event, or idea than this civil rights development. It helped push the United States toward a broader definition of citizenship and equal rights.",
  "after": "Both A and B were immediate consequences of King's assassination. It helped push the United States toward a broader definition of citizenship and equal rights."
}
```

### `us-58-x025` · US.58 · key-contradiction

**The key is A. Delete this intruding sentence? Read the AFTER text — if it still says why A is right, this is a yes.**

> The social movements of the late 1960s collectively challenged American society by —

*Checked:*
- key is 'A'; key text is 'Demonstrating that the promise of American democracy had not been extended equal'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "A is incorrect because it describes a different program, event, or idea than the topic in the question.",
  "before": "The social movements of the late 1960s collectively challenged American society by: both A and C describe the collective significance of 1960s social movements. A is incorrect because it describes a different program, event, or idea than the topic in the question. It shows how postwar America balanced reform, protest, and global responsibility.",
  "after": "The social movements of the late 1960s collectively challenged American society by: both A and C describe the collective significance of 1960s social movements. It shows how postwar America balanced reform, protest, and global responsibility."
}
```

### `us-71-x025` · US.64 · key-contradiction

**The key is B. Delete this intruding sentence? Read the AFTER text — if it still says why B is right, this is a yes.**

> The NSA's PRISM surveillance program, revealed by Snowden, collected data primarily from —

*Checked:*
- key is 'B'; key text is 'Major internet and technology companies — including Google, Facebook, and Apple '
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "B is wrong because the program was broader than targeted individual warrants.",
  "before": "PRISM collected data from major internet companies such as Google, Facebook, and Apple under secret surveillance programs revealed by Snowden. B is wrong because the program was broader than targeted individual warrants. The revelation showed how far post-9/11 surveillance had expanded into digital life.",
  "after": "PRISM collected data from major internet companies such as Google, Facebook, and Apple under secret surveillance programs revealed by Snowden. The revelation showed how far post-9/11 surveillance had expanded into digital life."
}
```

### `us-72-x015` · US.92 · key-contradiction

**The key is D. Delete this intruding sentence? Read the AFTER text — if it still says why D is right, this is a yes.**

> Secretary of State Colin Powell's February 2003 presentation to the UN Security Council on Iraqi WMDs is historically significant because —

*Checked:*
- key is 'D'; key text is "Powell later called it a 'blot' on his record after the WMD claims proved false"
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "D is wrong because the speech did not persuade France and Russia to support the invasion.",
  "before": "Colin Powell's 2003 UN speech became historically important because the WMD claims he presented later proved false, and Powell himself called it a stain on his record. D is wrong because the speech did not persuade France and Russia to support the invasion. The moment became a symbol of faulty intelligence and overconfidence before the war.",
  "after": "Colin Powell's 2003 UN speech became historically important because the WMD claims he presented later proved false, and Powell himself called it a stain on his record. The moment became a symbol of faulty intelligence and overconfidence before the war."
}
```

### `us-73-x023` · US.66 · key-contradiction

**The key is A. Delete this intruding sentence? Read the AFTER text — if it still says why A is right, this is a yes.**

> The Stafford Act governs FEMA's authority to respond to disasters. Katrina revealed its limitations because —

*Checked:*
- key is 'A'; key text is 'The Act required a congressional vote before FEMA could deploy resources exceedi'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "A is wrong because Congress did not need to vote before FEMA could spend major disaster funds.",
  "before": "Katrina showed that disaster law could delay federal action because FEMA depended heavily on formal state requests and clear lines of authority before moving fully. A is wrong because Congress did not need to vote before FEMA could spend major disaster funds. The storm exposed how rigid federal rules can slow response in a fast-moving catastrophe.",
  "after": "Katrina showed that disaster law could delay federal action because FEMA depended heavily on formal state requests and clear lines of authority before moving fully. The storm exposed how rigid federal rules can slow response in a fast-moving catastrophe."
}
```

### `us-74-q02` · US.92 · key-contradiction

**The key is B. Delete this intruding sentence? Read the AFTER text — if it still says why B is right, this is a yes.**

> The 2008 financial crisis was rooted in a housing bubble inflated by risky mortgage lending. 'Subprime' mortgages were bundled into complex financial instruments (mortgage-backed securities) and sold to investors worldwide. When housing prices fell, these instruments became worthless. This crisis de…

*Checked:*
- key is 'B'; key text is 'Deregulation of the financial industry in the 1990s and 2000s had removed safegu'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "B is wrong because banks still had legal disclosure obligations, and C is wrong because the lesson was not that all financial innovation is inherently bad.",
  "before": "The crisis suggested that decades of financial deregulation had removed safeguards and encouraged reckless risk-taking in housing and banking. B is wrong because banks still had legal disclosure obligations, and C is wrong because the lesson was not that all financial innovation is inherently bad. The crash sparked renewed debates over how tightly Wall Street should be regulated.",
  "after": "The crisis suggested that decades of financial deregulation had removed safeguards and encouraged reckless risk-taking in housing and banking. The crash sparked renewed debates over how tightly Wall Street should be regulated."
}
```

### `us-91-x028` · US.90 · key-contradiction

**The key is B. Delete this intruding sentence? Read the AFTER text — if it still says why B is right, this is a yes.**

> China's admission to the World Trade Organization (2001) had long-term consequences including:

*Checked:*
- key is 'B'; key text is 'A massive transfer of American technology to China that accelerated its military'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "B is incorrect because it points to a different Cold War policy or country; D is incorrect because it points to a different Cold War policy or country.",
  "before": "The WTO is important because it gives countries a formal process for settling trade disputes through international rulings instead of pure retaliation. B is incorrect because it points to a different Cold War policy or country; D is incorrect because it points to a different Cold War policy or country. It also reflects the larger debate over trade, jobs, and the proper size of the federal government.",
  "after": "The WTO is important because it gives countries a formal process for settling trade disputes through international rulings instead of pure retaliation. It also reflects the larger debate over trade, jobs, and the proper size of the federal government."
}
```

### `us-93-x015` · US.92 · key-contradiction

**The key is D. Delete this intruding sentence? Read the AFTER text — if it still says why D is right, this is a yes.**

> The increasing diversity of the Supreme Court over the past 50 years reflects:

*Checked:*
- key is 'D'; key text is 'Changing political priorities of presidents who recognized the symbolic and prac'
- the sentence is a distractor rationale left pointing at the old letter
- after deletion the rationale is still 2 finished sentence(s) and ends on terminal punctuation
- the RENDERED form is already correct — remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — a claim about history
- whether the remaining sentences say enough about why the key is right
- whether the REMAINING text is itself sound — this pass checks that a finished argument survives the deletion, not that it reads well. At least one item's remainder is mangled prose ('highlights city became major center steel production'), which no gate here detects

*Draft (not applied):*
```json
{
  "action": "delete one sentence",
  "delete": "B is incorrect because it names a different institution or power than the one the item asks about; D is incorrect because it names a different institution or power than the one the item asks about.",
  "before": "A more diverse Supreme Court reflects changing priorities in presidential appointments and the belief that the judiciary should not be limited to one social group. B is incorrect because it names a different institution or power than the one the item asks about; D is incorrect because it names a different institution or power than the one the item asks about. It also helps explain how symbolic breakthroughs can change who Americans imagine in positions of power.",
  "after": "A more diverse Supreme Court reflects changing priorities in presidential appointments and the belief that the judiciary should not be limited to one social
```

## Needs you — no machine can settle these

### `PSTIM-0166` · US.59 · authored-content

**Is the history in this item and its rationales correct, and would you give it to your students?**

> Use the photograph to answer the question. This photograph shows the signing ceremony for the North Atlantic Treaty on April 4, 1949. The treaty created the North Atlantic Treaty Organization (NATO), a mutual defense alliance between the United States, Canada, and ten Western European nations. (Phot…

*Checked:*
- structural gates pass on this item (record, key, distractors, relevance)

*Could NOT check:*
- every historical assertion in the stem, the key explanation and each distractor rationale — no gate can check any of them

### `PSTIM-0167` · US.59 · authored-content

**Is the history in this item and its rationales correct, and would you give it to your students?**

> Use the photograph to answer the question. This photograph shows the NATO treaty signing, April 4, 1949. (Photograph, 1949. Public Domain.) How did the creation of NATO, shown in this photograph, represent a departure from traditional American foreign policy?

*Checked:*
- structural gates pass on this item (record, key, distractors, relevance)

*Could NOT check:*
- every historical assertion in the stem, the key explanation and each distractor rationale — no gate can check any of them

### `U7-DOK2-0005` · US.59 · authored-content

**Is the history in this item and its rationales correct, and would you give it to your students?**

> How did the formation of NATO and the Warsaw Pact reflect the ideological competition between the United States and the Soviet Union during the Cold War?

*Checked:*
- structural gates pass on this item (record, key, distractors, relevance)

*Could NOT check:*
- every historical assertion in the stem, the key explanation and each distractor rationale — no gate can check any of them

### `US.05-GEN-01` · US.05 · authored-content

**Is the history in this item and its rationales correct, and would you give it to your students?**

> What did the Dawes Act of 1887 do to tribal land?

*Checked:*
- structural gates pass on this item (record, key, distractors, relevance)

*Could NOT check:*
- every historical assertion in the stem, the key explanation and each distractor rationale — no gate can check any of them

### `US.05-GEN-02` · US.05 · authored-content

**Is the history in this item and its rationales correct, and would you give it to your students?**

> Boarding schools for American Indians were designed primarily to —

*Checked:*
- structural gates pass on this item (record, key, distractors, relevance)

*Could NOT check:*
- every historical assertion in the stem, the key explanation and each distractor rationale — no gate can check any of them

### `q-us59-dok1-4` · US.59 · authored-content

**Is the history in this item and its rationales correct, and would you give it to your students?**

> What was the satellite state system in Eastern Europe?

*Checked:*
- structural gates pass on this item (record, key, distractors, relevance)

*Could NOT check:*
- every historical assertion in the stem, the key explanation and each distractor rationale — no gate can check any of them

### `q-us2-dok4-cr2` · US.23 · rubric-descriptor

**Do these bands describe what you would actually accept at each score?**

> Analyze how American imperialism in the late 1800s reflected BOTH idealistic and self-interested motivations. Use evidence from at least THREE specific events or policies (e.g., Spanish-American War, annexation of Hawaii, Open Door Policy, Panama Canal, Philippine-American War). Then evaluate whethe…

*Checked:*
- scale is well-formed: 0-4, every band has a descriptor

*Could NOT check:*
- what a strong answer contains is a pedagogical AND historical claim — policy alwaysEscalates any rubric descriptor

*Draft (not applied):*
```json
{
  "scorePoints": 4,
  "criteria": [
    {
      "points": 4,
      "descriptor": "Names THREE specific events or policies (e.g. the Spanish-American War, the annexation of Hawaii, the Open Door Policy, the Panama Canal, the Philippine-American War) and shows each carrying BOTH an idealistic justification and a self-interested motive — not three examples of one and none of the other. Quotes or closely paraphrases the era's own language (\"civilization\", \"duty\", \"markets\", \"coaling stations\") rather than asserting motive. The evaluation takes a clear position on whether imperialism strengthened or weakened American democratic ideals and defends it against the strongest objection to it, most often the Philippines."
    },
    {
      "points": 3,
      "descriptor": "Three specific examples, accurate, with both motive types present across the response even if one example carries on
```

### `q-us3-dok4-cr3` · US.46 · rubric-descriptor

**Do these bands describe what you would actually accept at each score?**

> Design a "New Deal Report Card" that grades THREE specific programs on two criteria: (1) effectiveness in addressing the immediate crisis, and (2) long-term impact on American government and society. For each program, assign a letter grade (A-F) for each criterion and justify your grading with speci…

*Checked:*
- scale is well-formed: 0-4, every band has a descriptor

*Could NOT check:*
- what a strong answer contains is a pedagogical AND historical claim — policy alwaysEscalates any rubric descriptor

*Draft (not applied):*
```json
{
  "scorePoints": 4,
  "criteria": [
    {
      "points": 4,
      "descriptor": "Grades THREE named New Deal programs on BOTH criteria separately, and the two grades come apart for at least one program — the response shows it understands that immediate relief and long-term structural change are different achievements (the CCC put men to work quickly and left little institutional legacy; Social Security did comparatively little in 1935 and reshaped the federal government permanently). Every grade is justified with specific evidence: enrollment or spending figures, dates, what the programme actually did, what a court or Congress did to it."
    },
    {
      "points": 3,
      "descriptor": "Three named programs graded on both criteria with accurate supporting evidence. Grades are defended. The short-term/long-term distinction is present but the two grades largely track each other."
  
```

### `q-us6-dok4-cr1` · US.59 · rubric-descriptor

**Do these bands describe what you would actually accept at each score?**

> The Cold War was fought through proxies, propaganda, espionage, and economic competition rather than direct military conflict between the U.S. and Soviet Union. Analyze WHY the Cold War took this form by examining at least THREE factors that prevented direct conflict. Then evaluate whether this "col…

*Checked:*
- scale is well-formed: 0-4, every band has a descriptor

*Could NOT check:*
- what a strong answer contains is a pedagogical AND historical claim — policy alwaysEscalates any rubric descriptor

*Draft (not applied):*
```json
{
  "scorePoints": 4,
  "criteria": [
    {
      "points": 4,
      "descriptor": "Analyses THREE distinct factors that kept the superpowers from direct conflict — nuclear deterrence and the logic of mutual assured destruction, the alliance and bloc structure that made escalation collective, and the diplomatic channels and norms that developed for managing crises — and explains the MECHANISM of each, not just its name. The evaluation confronts the real difficulty: the \"cold\" form avoided a great-power war while producing enormous casualties in Korea, Vietnam and elsewhere, so \"less dangerous\" and \"more dangerous\" depend on who is counted. A position is taken and defended."
    },
    {
      "points": 3,
      "descriptor": "Three factors, accurately identified, with at least two explained mechanically. The evaluation takes a position and offers support, but treats the proxy-war c
```

### `q-us6-dok4-cr3` · US.60 · rubric-descriptor

**Do these bands describe what you would actually accept at each score?**

> Compare the Marshall Plan (1948) with modern American foreign aid programs. What principles from the Marshall Plan's success could be applied to current challenges? What limitations would such an approach face today?

*Checked:*
- scale is well-formed: 0-4, every band has a descriptor

*Could NOT check:*
- what a strong answer contains is a pedagogical AND historical claim — policy alwaysEscalates any rubric descriptor

*Draft (not applied):*
```json
{
  "scorePoints": 4,
  "criteria": [
    {
      "points": 4,
      "descriptor": "Identifies specific principles behind the Marshall Plan's success — its scale, its requirement that recipients cooperate and plan jointly, and the alignment of American economic self-interest with European recovery — and applies them to a NAMED contemporary aid context rather than to foreign aid in general. The limitations are historically grounded: post-war Europe had industrial capacity and institutions to rebuild, the aid ran through a bipartisan Cold War consensus, and the recipients were states that wanted it. Comparison runs in both directions; it does not simply recommend repeating the Plan."
    },
    {
      "points": 3,
      "descriptor": "Names at least two real principles and applies them to a contemporary context with reasonable specificity. Limitations are identified and plausible, if not 
```
