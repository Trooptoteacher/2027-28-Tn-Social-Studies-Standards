# Review worksheet — AI first pass

**Nothing here is approved.** Every row is a recommendation with its evidence and what it could not check. `aiReview` counts toward no gate and lets nothing ship — your decision is still the only one that settles anything.

- **79** recommended for a fast confirm
- **30** with a bounded fix drafted (not applied)
- **10** that need your judgement

Record decisions in `reviewed/ai-review.json` (`humanVerdict` per row), then apply approvals through `tools/apply_review.py` as usual.

## Fast confirm — checked against a source of truth in the repo

### `q-us01-dok4-cr-1` · US.04, US.05, US.08 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from the 13th Amendment to the United States Constitution, ratified December 6, 1865 (National Archives, Record Group 11): "Section 1. Neither slavery nor involuntary servitude, except as a punishment for crime whereof the party shall have been duly convicted, shall exist …

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us08-dok4-cr-1` · US.11, US.12 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from Andrew Carnegie's essay "The Gospel of Wealth" (1889), published in the North American Review (available through the Library of Congress digital collections): "The problem of our age is the proper administration of wealth, so that the ties of brotherhood may still bin…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us09-dok4-cr-2` · US.16 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from Jacob Riis, How the Other Half Lives: Studies Among the Tenements of New York (1890), available through the Library of Congress digital collections: "Suppose we look into one of these houses... We find two, perhaps three, families on a floor, each in a room or two, wi…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us09-dok4-dbq-2` · US.06, US.15, US.18 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION Directions: Analyze each of the following three documents using the SOAPS framework (Speaker, Occasion, Audience, Purpose, Significance). Then construct a well-organized argument that responds to the prompt. PROMPT: How effectively did Progressive Era reformers respond to the…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us10-dok4-cr-8` · US.06, US.14 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from Jane Addams, Twenty Years at Hull-House (1910), available in the public domain through the Library of Congress and Project Gutenberg: "Hull-House was established not as a social experiment, but because of the sincere conviction that the first step toward meeting the s…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us11-dok4-cr-3` · US.13, US.14 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from the Report of the Factory Investigating Commission of the State of New York (1912), established in the aftermath of the Triangle Shirtwaist Factory fire of March 25, 1911 (available through the New York State Library and the National Archives): "The fire at the Triang…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us11-dok4-dbq-6` · US.11, US.13, US.14 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION Directions: Analyze each document using the HIPP framework. Then construct a well-organized argument that responds to the prompt. PROMPT: Some historians argue that the Progressive Era's labor reforms were genuine structural achievements; others argue they were minimal conces…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us14-dok4-cr-4` · US.16, US.18 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from Upton Sinclair, The Jungle (1906), available in the public domain through Project Gutenberg and the Library of Congress: "There was never the least attention paid to what was cut up for sausage; there would come all the way back from Europe old sausage that had been r…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us14-dok4-dbq-4` · US.16, US.18, US.20 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION Directions: Analyze each document using the HIPP framework. Then construct a well-organized argument that responds to the prompt. PROMPT: Muckraker journalism is often credited with driving Progressive Era reform. Using all three documents and at least two outside historical …

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us16-dok4-cr-5` · US.17, US.18 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from the text of the Nineteenth Amendment to the United States Constitution, ratified August 18, 1920 (National Archives, Washington, D.C.): "The right of citizens of the United States to vote shall not be denied or abridged by the United States or by any State on account …

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us16-dok4-dbq-5` · US.17, US.18, US.19 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION Directions: Analyze each document using the SOAPS framework. Then construct a well-organized argument that responds to the prompt. PROMPT: The Progressive Era (1890-1920) has been characterized as a period of democratic expansion. Using all three documents and at least two ou…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us18-dok4-cr-7` · US.13, US.20 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from Theodore Roosevelt, "The New Nationalism" speech delivered at Osawatomie, Kansas, August 31, 1910, and published by the National Archives: "The man who wrongly holds that every human right is secondary to his profit must now give way to the advocate of human welfare, …

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us19-dok4-cr-1` · US.21, US.22 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from Alfred Thayer Mahan, The Influence of Sea Power Upon History (1890), published by Avalon Project, Yale Law School (avalon.law.yale.edu), and Company, Boston — public domain: "The due use and control of the sea is but one link in the chain of exchange by which wealth a…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us20-dok4-cr-2` · US.22, US.23 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from President William McKinley's War Message to Congress, April 11, 1898 (Bryan, William Jennings, ed., Republic or Empire (1899), public domain — public domain): "The war in Cuba is of such a nature that, short of subjugation or extermination, a final military victory fo…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us20-dok4-dbq-2` · US.22, US.23 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Document-Based Question: The Spanish-American War and the Question of Empire, 1898 Directions: Read the three documents below. Then write a well-organized essay that constructs an argument addressing the following question: Did the Spanish-American War represent a turning point in American foreign p…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us22-dok4-cr-4` · US.23 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from President Theodore Roosevelt's Annual Message to Congress, December 7, 1903, regarding the Panama Canal (Bryan, William Jennings, ed., Republic or Empire (1899), public domain — public domain): "No single great material work which remains to be undertaken on this cont…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us23-dok4-dbq-3` · US.21, US.25 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Document-Based Question: Big Stick Diplomacy and the Monroe Doctrine, 1823–1904 Directions: Read the two documents below. Then write a well-organized essay addressing the following question: How did the Roosevelt Corollary transform the Monroe Doctrine from a defensive statement into an instrument o…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us24-dok4-cr-5` · US.26, US.27 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from President Woodrow Wilson's Address to Congress Requesting a Declaration of War, April 2, 1917 (Bryan, William Jennings, ed., Republic or Empire (1899), public domain — public domain): "It is a fearful thing to lead this great peaceful people into war, into the most di…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us25-dok4-dbq-4` · US.26, US.27 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Document-Based Question: The Road to War — American Neutrality and Entry into World War I, 1914–1917 Directions: Read the three documents below. Then write a well-organized essay addressing the following question: To what extent was U.S. entry into World War I in April 1917 a response to deliberate …

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us26-dok4-cr-6` · US.26, US.28 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from Schenck v. United States, Supreme Court of the United States, March 3, 1919 (public domain — U.S. government document): "The question in every case is whether the words used are used in such circumstances and are of such a nature as to create a clear and present dange…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us26-dok4-dbq-5` · US.27, US.28 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Document-Based Question: Civil Liberties and the Home Front in World War I Directions: Read the two documents below. Then write a well-organized essay addressing the following question: How did the U.S. government's management of the home front during World War I reveal fundamental tensions between …

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us27-dok4-cr-7` · US.26, US.29 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from Senator Henry Cabot Lodge's speech opposing the League of Nations, August 12, 1919 (Bryan, William Jennings, ed., Republic or Empire (1899), public domain — public domain): "I have loved but one flag and I can not share that devotion and give affection to the mongrel …

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us27-dok4-dbq-6` · US.26, US.29 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Document-Based Question: Peacemaking and Its Consequences — The Treaty of Versailles and the Fourteen Points, 1918–1919 Directions: Read the three documents below. Then write a well-organized essay addressing the following question: To what extent did the Treaty of Versailles fulfill, compromise, or…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us28-dok4-cr-1` · US.37 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from U.S. Attorney General A. Mitchell Palmer, "The Case Against the Reds," published in Records of the Department of Justice, National Archives (archives.gov), February 1920 (National Archives, Record Group 60 (archives.gov), public domain): "Like a prairie-fire, the blaz…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us28-dok4-dbq-1` · US.37 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following two primary source excerpts and answer the prompt below. ───────────────────────────────────────── DOCUMENT A A. Mitchell Palmer, U.S. Attorney General, "The Case Against the Reds," Records of the Department of Justice, National Archives (archives.gov), February 1920 (National Arc…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us29-dok4-dbq-2` · US.37 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following two primary source excerpts and answer the prompt below. ───────────────────────────────────────── DOCUMENT A Immigration Act of 1924 (Johnson-Reed Act), Section 11, U.S. Statutes at Large, 68th Congress (public domain): "The annual quota of any nationality shall be two per centum…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us30-dok4-cr-2` · US.39 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from the Volstead Act (National Prohibition Act), Title II, Section 3, enacted October 28, 1919 (U.S. Statutes at Large, 66th Congress, public domain): "No person shall on or after the date when the eighteenth amendment to the Constitution of the United States goes into ef…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us31-dok4-cr-3` · US.38 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from the transcript of State of Tennessee v. John T. Scopes (Rhea County Circuit Court, Dayton, Tennessee, July 1925), during Clarence Darrow's cross-examination of William Jennings Bryan, July 20, 1925 (trial transcript, public domain, Library of Congress collection): "DA…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us31-dok4-dbq-3` · US.38 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following three primary source excerpts and answer the prompt below. ───────────────────────────────────────── DOCUMENT A Tennessee Butler Act, Chapter 27, House Bill 185, enacted March 21, 1925 (Tennessee Acts, 64th General Assembly, public domain): "An Act prohibiting the teaching of the …

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us31-dok4-dbq-8` · US.38 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following two primary source excerpts and answer the prompt below. ───────────────────────────────────────── DOCUMENT A William Jennings Bryan, closing statement prepared for the Scopes Trial, Dayton, Tennessee, 1925 (Bryan never delivered this statement — the trial ended before the defense…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us33-dok4-cr-5` · US.35 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from President Calvin Coolidge, address to the American Society of Newspaper Editors, Washington, D.C., January 17, 1925 (Congressional Record / White House press release, public domain): "The chief business of the American people is business. They are profoundly concerned…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us34-dok4-dbq-6` · US.36, US.37, US.38 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following two primary source excerpts and answer the prompt below. ───────────────────────────────────────── DOCUMENT A Calvin Coolidge, address to the American Society of Newspaper Editors, Washington, D.C., January 17, 1925 (White House press release / Congressional Record, public domain)…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us35-dok4-cr-6` · US.30, US.31, US.37, US.38 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from Warren G. Harding, "Return to Normalcy" campaign speech, Boston, Massachusetts, May 14, 1920 (Congressional Record, public domain): "America's present need is not heroics but healing; not nostrums but normalcy; not revolution but restoration; not agitation but adjustm…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us35-dok4-dbq-7` · US.37 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following three primary source excerpts and answer the prompt below. ───────────────────────────────────────── DOCUMENT A Warren G. Harding, "Return to Normalcy" campaign speech, Boston, Massachusetts, May 14, 1920 (Congressional Record, public domain): "America's present need is not heroic…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us38-dok4-cr-9` · US.37 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from the Statement of Bartolomeo Vanzetti after sentencing to death, Norfolk County Superior Court, April 9, 1927 (court records, public domain): "I am suffering because I am a radical and indeed I am a radical; I have suffered because I was an Italian, and indeed I am an …

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us39-dok4-cr-1` · US.41, US.42 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from Herbert Hoover's address to the United States Chamber of Commerce, May 1, 1930 (National Archives, public domain): "The fundamental business of the country — that is, production and distribution of commodities — is on a sound and prosperous basis. The difficulty is la…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us39-dok4-cr-6` · US.37, US.38, US.41 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from the Report of the Committee on Banking and Currency, U.S. Senate, investigating the causes of the stock market crash, 1931 (U.S. Government Printing Office, public domain): "The decade of the nineteen-twenties saw a vast increase in the use of credit for the purchase …

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us39-dok4-dbq-1` · US.41, US.42, US.43 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION Directions: Analyze the three primary sources below. Then respond to the prompt using evidence from ALL THREE documents and your own historical knowledge. --- DOCUMENT A Herbert Hoover, Press Statement on the Economy, October 25, 1929 (National Archives, public domain): "The …

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us40-dok4-cr-2` · US.41, US.42 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Study the following description of Dorothea Lange's photograph "Migrant Mother" (1936), held in the Library of Congress Farm Security Administration collection (public domain): The photograph depicts Florence Owens Thompson, a 32-year-old pea picker in Nipomo, California. Her crop had been destroyed…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us41-dok4-cr-3` · US.43, US.46 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from Franklin D. Roosevelt's Second Inaugural Address, January 20, 1937 (National Archives, public domain): "I see one-third of a nation ill-housed, ill-clad, ill-nourished... The test of our progress is not whether we add more to the abundance of those who have much; it i…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us41-dok4-dbq-4` · US.43, US.45, US.46 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION Directions: Analyze the three primary sources below. Then respond to the prompt using evidence from ALL THREE documents and your own historical knowledge. --- DOCUMENT A National Industrial Recovery Act, Section 1 (Declaration of Policy), June 16, 1933 (National Archives, pub…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us42-dok4-cr-4` · US.43, US.44 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from the Tennessee Valley Authority Act, signed by President Franklin D. Roosevelt on May 18, 1933 (National Archives, public domain): "Be it enacted...that there is hereby created a body corporate by the name of the 'Tennessee Valley Authority'...The President is authoriz…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us42-dok4-dbq-2` · US.43, US.44, US.45 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION Directions: Analyze the three primary sources below. Then respond to the prompt using evidence from ALL THREE documents and your own historical knowledge. --- DOCUMENT A Tennessee Valley Authority Act, Section 1, May 18, 1933 (National Archives, public domain): "Be it enacted…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us43-dok4-cr-5` · US.43, US.45 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from the National Labor Relations Act (Wagner Act), signed July 5, 1935 (National Archives, public domain): "It is hereby declared to be the policy of the United States to eliminate the causes of certain substantial obstructions to the free flow of commerce...by encouragin…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us44-dok4-dbq-3` · US.43, US.46 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION Directions: Analyze the three primary sources below. Then respond to the prompt using evidence from ALL THREE documents and your own historical knowledge. --- DOCUMENT A Huey Long, "Share Our Wealth" Radio Address, February 23, 1934 (Congressional Record, public domain): "How…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us45-dok4-cr-1` · US.47, US.48 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from Franklin D. Roosevelt's "Four Freedoms" speech, delivered to Congress on January 6, 1941 (National Archives, public domain): "In the future days, which we seek to make secure, we look forward to a world founded upon four essential human freedoms. The first is freedom …

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us45-dok4-dbq-1` · US.47, US.48 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Analyze the following three primary source excerpts and write a document-based essay that argues whether the policy of appeasement and American isolationism made World War II inevitable. DOCUMENT A: Excerpt from the Atlantic Charter, signed by FDR and Winston Churchill, August 14, 1941 (National Arc…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us46-dok4-cr-2` · US.48, US.49 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from the Neutrality Act of 1937, a U.S. government document (public domain, available through the Avalon Project, Yale Law School): "Whenever the President shall find that there exists a state of war between, or among, two or more foreign states, the President shall procla…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us46-dok4-dbq-2` · US.48, US.49 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Using the following two primary sources, construct a document-based argument that analyzes how Pearl Harbor transformed American public opinion and government policy from isolationism to total war mobilization. DOCUMENT A: Excerpt from President Franklin D. Roosevelt's 'Day of Infamy' address to Con…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us53-dok4-cr-9` · US.51, US.52 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following editorial excerpt from the Executive Order 8802 records (National Archives), February 14, 1942, launching Executive Order 8802 and the Fair Employment Practices Committee (Federal Register, Vol. 6, No. 125, June 25, 1941; National Archives, archives.gov): "We call upon the Preside…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us53-dok4-dbq-5` · US.51, US.52 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Analyze the following two primary source excerpts and construct a document-based argument about the contradictions African Americans faced during World War II and how those contradictions shaped postwar civil rights activism. DOCUMENT A: Excerpt from the Executive Order 8802, President Franklin D. R…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us54-dok4-cr-10` · US.48, US.54 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from Justice Robert Jackson's dissent in Korematsu v. United States, 323 U.S. 214 (1944) (Supreme Court of the United States, public domain): "A military order, however unconstitutional, is not apt to last longer than the military emergency. Even during that period a succe…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us54-dok4-dbq-6` · US.48, US.54 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Analyze the following two primary source excerpts and construct a document-based argument about the constitutional crisis created by Japanese American internment. DOCUMENT A: Excerpt from Executive Order 9066, issued by President Franklin D. Roosevelt, February 19, 1942 (Federal Register, 1942; Nati…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us59-dok4-cr-1` · US.59, US.60 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from George Kennan's "The Sources of Soviet Conduct" (the 'X Article'), published in Foreign Affairs, July 1947 — a article published anonymously in Foreign Affairs (July 1947), later declassified as authored by George F. Kennan available through the Avalon Project, Yale L…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us59-dok4-dbq-1` · US.60 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION: The Origins of the Cold War Directions: Read the following three primary source excerpts and then respond to the prompt below. In your response, analyze each document using the HIPP framework (Historical context, Intended audience, Purpose, Point of view) and construct an ev…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us60-dok4-cr-2` · US.60, US.61 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from President Harry S. Truman's Address to Congress, March 12, 1947 — a U.S. government document available through the Avalon Project, Yale Law School, and the National Archives: "I believe that it must be the policy of the United States to support free peoples who are re…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us61-dok4-dbq-2` · US.59, US.63 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION: The Marshall Plan — Economic Aid as Cold War Strategy Directions: Read the following two primary source excerpts and then respond to the prompt below. Analyze both documents using the SOAPS framework (Speaker, Occasion, Audience, Purpose, Significance) and construct an evide…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us62-dok4-dbq-3` · US.60 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION: Berlin and NATO — The Crystallization of the Cold War Alliance System Directions: Read the following three primary source excerpts and respond to the prompt below. Apply HIPP analysis to at least two documents and construct an argument. --- DOCUMENT A: President Harry S. Tru…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us63-dok4-cr-3` · US.60, US.62 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from NSC-68: United States Objectives and Programs for National Security, April 14, 1950 — a declassified U.S. National Security Council document available through the National Archives: "The issues that face us are momentous, involving the fulfillment or destruction not o…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us64-dok4-cr-4` · US.63 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from Senator Joseph McCarthy's speech to the Senate, June 14, 1951, Congressional Record — a U.S. government document available through the National Archives: "How can we account for our present situation unless we believe that men high in this government are concerting to…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us66-dok4-cr-5` · US.70 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from President John F. Kennedy's letter to Premier Nikita Khrushchev, October 27, 1962 — a declassified U.S. government document available through the National Archives and the John F. Kennedy Presidential Library: "You would agree to remove these weapons systems from Cuba…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us66-dok4-dbq-5` · US.70 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION: The Cuban Missile Crisis — Nuclear Brinkmanship and Diplomatic Resolution Directions: Read the following three primary source excerpts and respond to the prompt below. Apply HIPP analysis to at least two documents and construct an argument. --- DOCUMENT A: President John F. …

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us67-dok4-cr-6` · US.62 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from President Dwight D. Eisenhower's Farewell Address to the Nation, January 17, 1961 — a U.S. government document available through the Avalon Project, Yale Law School, and the National Archives: "In the councils of government, we must guard against the acquisition of un…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us71-dok4-cr-1` · US.74 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from the U.S. Supreme Court's unanimous decision in Brown v. Board of Education (1954), written by Chief Justice Earl Warren. Source: Brown v. Board of Education, 347 U.S. 483 (1954), National Archives, archives.gov. "We conclude that, in the field of public education, the…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us71-dok4-dbq-1` · US.64, US.66 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION Directions: Analyze the following three primary sources. For each document, apply the HIPP framework (Historical context, Intended audience, Purpose, Point of view). Then construct a written argument that addresses the central question: To what extent did the legal dismantlin…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us72-dok4-cr-2` · US.77 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from the U.S. Supreme Court's decision in Browder v. Gayle, 352 U.S. 903 (1956), affirming the lower court ruling that declared Montgomery's bus segregation unconstitutional. Source: Browder v. Gayle, United States District Court for the Middle District of Alabama (1956), …

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us72-dok4-dbq-2` · US.78 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION Directions: Analyze the following two primary sources using the SOAPS framework (Speaker, Occasion, Audience, Purpose, Significance) for each document. Then construct a multi-paragraph argument responding to the central question: How did the Montgomery Bus Boycott redefine th…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us73-dok4-cr-3` · US.50 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from President Dwight D. Eisenhower's radio and television address to the nation on the situation in Little Rock, Arkansas, September 24, 1957. Source: Public Papers of the Presidents of the United States: Dwight D. Eisenhower, 1957, U.S. Government Printing Office; availa…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us74-dok4-cr-4` · US.76 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> The Nashville sit-in campaign of 1960 is recognized as one of the most strategically disciplined and philosophically sophisticated direct-action campaigns in the Civil Rights Movement. Diane Nash, a Nashville native and Fisk University student, emerged as a central organizer. The following excerpt i…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us75-dok4-dbq-4` · US.76 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION Directions: Analyze the following two primary sources using the HIPP framework (Historical context, Intended audience, Purpose, Point of view) for each document. Then construct a multi-paragraph argument responding to the central question: How did civil rights leaders at the …

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us76-dok4-cr-5` · US.76 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from the Civil Rights Act of 1964, Title II (Public Accommodations) and Title VII (Equal Employment Opportunity). Source: Civil Rights Act of 1964, Pub. L. 88-352, 78 Stat. 241, July 2, 1964; National Archives, archives.gov. Title II, Section 201(a): "All persons shall be …

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us77-dok4-dbq-5` · US.78 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION Directions: Analyze the following two primary sources using the HIPP framework (Historical context, Intended audience, Purpose, Point of view) for each document. Then construct a multi-paragraph argument responding to the central question: How did the Voting Rights Act of 196…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us78-dok4-cr-1` · US.80 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from the Gulf of Tonkin Resolution, passed by Congress on August 7, 1964 (Joint Resolution of Congress H.J. RES 1145, 88th Congress, 2d Session, August 7, 1964; National Archives, Record Group 46): "Resolved by the Senate and House of Representatives of the United States o…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us79-dok4-dbq-2` · US.76, US.79 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DIRECTIONS: Analyze the three primary source excerpts below. Then write a response that constructs a historical argument answering the following question: How did the convergence of the anti-war movement, the Kent State killings, and the Watergate crisis between 1969 and 1974 together erode public t…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us81-dok4-cr-3` · US.78, US.79 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from Title IX of the Education Amendments of 1972 (Public Law 92-318, 86 Stat. 373, signed June 23, 1972; text from the Public Law 92-318, U.S. Government Publishing Office / National Archives / National Archives): "No person in the United States shall, on the basis of sex…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us83-dok4-cr-1` · US.73, US.82 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from President Ronald Reagan's First Inaugural Address, delivered January 20, 1981 (Public domain; National Archives): "In this present crisis, government is not the solution to our problem; government is the problem. From time to time we've been tempted to believe that so…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us87-dok4-dbq-3` · US.88 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION: The Persian Gulf War and the New World Order Directions: Read the following two primary source excerpts. Using the HIPP framework and your knowledge of US.87, write a response that analyzes both documents and constructs an argument about the Persian Gulf War's significance a…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us92-dok4-cr-7` · US.90 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> Read the following excerpt from the USA PATRIOT Act (Uniting and Strengthening America by Providing Appropriate Tools Required to Intercept and Obstruct Terrorism), Public Law 107-56, signed October 26, 2001 (Public domain; U.S. Government Publishing Office): "The Director of the Federal Bureau of I…

*Checked:*
- all 5 bands (0-4) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

### `q-us92-dok4-dbq-6` · US.90 · rubric-extraction-fidelity

**Confirm this scoring guide is the one you want used.**

> DOCUMENT-BASED QUESTION: Civil Liberties in the War on Terror Era Directions: Read the following two primary source excerpts. Using the SOAPS framework and your knowledge of US.92, write a response that analyzes both documents and constructs an argument about the tension between national security an…

*Checked:*
- all 7 bands (0-6) appear verbatim in the item's own explanation text — extracted, not authored
- scale is complete and every band carries a descriptor

## Fix drafted — read the draft, then decide

### `US.01-X020` · US.04 · key-contradiction

**The key is D. Its explanation says: "Option D is incorrect because this ideology directly shaped federal land and military policy throughout the 19th century." — is the KEY still right, and if so what should this sentence say instead?**

> How did the ideology of Manifest Destiny shape U.S. policy toward American Indian peoples in the late 19th century?

*Checked:*
- key is 'D'; key text is 'It provided ideological justification for westward territorial expansion and the'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `US.01-X021` · US.04 · key-contradiction

**The key is A. Its explanation says: "Option A is incorrect because the Great Plains suffer from insufficient rainfall and drought, not flooding." — is the KEY still right, and if so what should this sentence say instead?**

> Which of the following best explains why farming on the Great Plains was especially difficult for homesteaders in the late 19th century?

*Checked:*
- key is 'A'; key text is 'Insufficient timber for construction, scarce water, periodic droughts, and hard '
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `q-new-us09-dok1-carnegie` · US.09 · key-contradiction

**The key is D. Its explanation says: "Choice D is wrong if it names oil, because that was Rockefeller’s field, not Carnegie’s." — is the KEY still right, and if so what should this sentence say instead?**

> Andrew Carnegie built his industrial fortune primarily in which industry?

*Checked:*
- key is 'D'; key text is 'Steel production and manufacturing for construction purposes'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `q-new-us09-dok2-rockefeller` · US.09 · key-contradiction

**The key is B. Its explanation says: "Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup." — is the KEY still right, and if so what should this sentence say instead?**

> John D. Rockefeller's Standard Oil Company was an example of —

*Checked:*
- key is 'B'; key text is 'A monopoly that controlled oil refining and distribution'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `q-tcap-us09-urbanization-1` · US.15 · key-contradiction

**The key is D. Its explanation says: "Choice D is wrong if it names oil, because that was Rockefeller’s field, not Carnegie’s." — is the KEY still right, and if so what should this sentence say instead?**

> Which city became a major center for steel production due to its location near coal and iron ore deposits?

*Checked:*
- key is 'D'; key text is 'Pittsburgh'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `q-us09-dok2-6` · US.09 · key-contradiction

**The key is B. Its explanation says: "Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup." — is the KEY still right, and if so what should this sentence say instead?**

> What business practice did John D. Rockefeller primarily use to build Standard Oil?

*Checked:*
- key is 'B'; key text is 'Horizontal integration - buying out competing oil refineries'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `q-us14-dok1-2-u2` · US.16 · key-contradiction

**The key is B. Its explanation says: "Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup." — is the KEY still right, and if so what should this sentence say instead?**

> What did Ida Tarbell's investigative reporting expose?

*Checked:*
- key is 'B'; key text is 'The monopolistic practices of Standard Oil Company'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `q-us14-dok1-tarbell` · US.16 · key-contradiction

**The key is B. Its explanation says: "Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup." — is the KEY still right, and if so what should this sentence say instead?**

> What company did Ida Tarbell expose in her investigative journalism?

*Checked:*
- key is 'B'; key text is 'Standard Oil'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `q-us73-add-2` · US.66 · key-contradiction

**The key is D. Its explanation says: "B is wrong because highways were a transportation change, not a medical advance, and D is wrong because it describes a broad result rather than the specific breakthrough." — is the KEY still right, and if so what should this sentence say instead?**

> What medical advance during the 1950s dramatically improved public health?

*Checked:*
- key is 'D'; key text is "Jonas Salk's polio vaccine, which nearly eliminated a feared childhood disease"
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `q-us73-add-3` · US.66 · key-contradiction

**The key is B. Its explanation says: "B is wrong because the polio vaccine had nothing to do with highway policy." — is the KEY still right, and if so what should this sentence say instead?**

> Which domestic objective helped Eisenhower justify the Interstate Highway System?

*Checked:*
- key is 'B'; key text is 'Improving civilian transportation while supporting national defense logistics'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `q-us75-add-3` · US.67 · key-contradiction

**The key is D. Its explanation says: "D is wrong because advertising shaped buying habits more than shared culture, and C is wrong because it focuses on campaigns." — is the KEY still right, and if so what should this sentence say instead?**

> How did television contribute to a more national popular culture in the 1950s?

*Checked:*
- key is 'D'; key text is 'Families across regions watched the same news, sports, and entertainment program'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `q-us76-add-5` · US.68 · key-contradiction

**The key is B. Its explanation says: "B is wrong because B.B." — is the KEY still right, and if so what should this sentence say instead?**

> How did Tennessee recording centers help shape youth culture in the 1950s?

*Checked:*
- key is 'B'; key text is 'Studios in Memphis and Nashville popularized crossover sounds that reached natio'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `q-us77-add-2` · US.72 · key-contradiction

**The key is D. Its explanation says: "D is wrong because it describes the New Frontier itself, not the effect of Kennedy's death." — is the KEY still right, and if so what should this sentence say instead?**

> How did Kennedy's assassination in 1963 affect American society?

*Checked:*
- key is 'D'; key text is 'It traumatized the nation and created sympathy that helped pass his legislative '
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `q-us77-add-5` · US.72 · key-contradiction

**The key is B. Its explanation says: "B is wrong because the Peace Corps was only one program, not the broader legacy." — is the KEY still right, and if so what should this sentence say instead?**

> How did New Frontier proposals influence later domestic policy even when not fully enacted under Kennedy?

*Checked:*
- key is 'B'; key text is 'They provided legislative foundations that Johnson advanced through Great Societ'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `q-us86-add-1` · US.84 · key-contradiction

**The key is A. Its explanation says: "A is incorrect because that refers to Watergate rather than the concept asked about here; D is incorrect because it names a different institution or power than the one the item asks about." — is the KEY still right, and if so what should this sentence say instead?**

> What was the Watergate scandal?

*Checked:*
- key is 'A'; key text is "A break-in at Democratic headquarters and Nixon's cover-up that led to his resig"
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `q-us93-3` · US.92 · key-contradiction

**The key is C. Its explanation says: "B is incorrect because it identifies a different historic barrier-breaking achievement; C is incorrect because it identifies a different historic barrier-breaking achievement." — is the KEY still right, and if so what should this sentence say instead?**

> What barrier did Nancy Pelosi break in American political history in 2007?

*Checked:*
- key is 'C'; key text is 'She became the first woman to serve as Speaker of the House'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `q-us93-add-3` · US.92 · key-contradiction

**The key is C. Its explanation says: "B is incorrect because it identifies a different historic barrier-breaking achievement; C is incorrect because it identifies a different historic barrier-breaking achievement." — is the KEY still right, and if so what should this sentence say instead?**

> Who was Nancy Pelosi and what was historic about her role?

*Checked:*
- key is 'C'; key text is 'She became the first woman to serve as Speaker of the House in 2007'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `us-09-x012` · US.16 · key-contradiction

**The key is B. Its explanation says: "Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup." — is the KEY still right, and if so what should this sentence say instead?**

> Ida Tarbell's investigation of Standard Oil (1904) was significant because it —

*Checked:*
- key is 'B'; key text is 'Documented through meticulous research how Rockefeller had used secret railroad '
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `us-09-x025` · US.16 · key-contradiction

**The key is B. Its explanation says: "Choice B is wrong if it points to the Clayton Act or another later law, because Tarbell’s work is most directly linked to the attack on Standard Oil that ended in the 1911 breakup." — is the KEY still right, and if so what should this sentence say instead?**

> Ida Tarbell's investigation of Standard Oil relied primarily on —

*Checked:*
- key is 'B'; key text is 'Public records, court documents, and interviews that Standard Oil believed were '
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `us-46-x022` · US.59 · key-contradiction

**The key is C. Its explanation says: "C is incorrect because it describes a different program, event, or idea than this Cold War development." — is the KEY still right, and if so what should this sentence say instead?**

> NATO (1949) was significant because it was —

*Checked:*
- key is 'C'; key text is 'The first peacetime military alliance in American history, entangling the U.S. i'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `us-46-x027` · US.48 · key-contradiction

**The key is A. Its explanation says: "A is incorrect because it describes a different program, event, or idea than the topic in the question." — is the KEY still right, and if so what should this sentence say instead?**

> MacArthur's dismissal by Truman in April 1951 was significant constitutionally because it affirmed —

*Checked:*
- key is 'A'; key text is 'The principle that generals could not advocate for different policies publicly w'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `us-54-x026` · US.54 · key-contradiction

**The key is C. Its explanation says: "C is incorrect because it describes a different program, event, or idea than this civil rights development." — is the KEY still right, and if so what should this sentence say instead?**

> The Albany Movement (1961-62) was considered a tactical failure for the Civil Rights Movement because —

*Checked:*
- key is 'C'; key text is 'The Kennedy administration refused to intervene, leaving protesters without fede'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `us-56-x024` · US.76 · key-contradiction

**The key is B. Its explanation says: "B is incorrect because it describes a different program, event, or idea than this civil rights development." — is the KEY still right, and if so what should this sentence say instead?**

> The assassination of Martin Luther King Jr. (April 4, 1968) triggered —

*Checked:*
- key is 'B'; key text is 'Congressional passage of the Civil Rights Act of 1968 (Fair Housing Act) within '
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `us-58-x025` · US.58 · key-contradiction

**The key is A. Its explanation says: "A is incorrect because it describes a different program, event, or idea than the topic in the question." — is the KEY still right, and if so what should this sentence say instead?**

> The social movements of the late 1960s collectively challenged American society by —

*Checked:*
- key is 'A'; key text is 'Demonstrating that the promise of American democracy had not been extended equal'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `us-71-x025` · US.64 · key-contradiction

**The key is B. Its explanation says: "B is wrong because the program was broader than targeted individual warrants." — is the KEY still right, and if so what should this sentence say instead?**

> The NSA's PRISM surveillance program, revealed by Snowden, collected data primarily from —

*Checked:*
- key is 'B'; key text is 'Major internet and technology companies — including Google, Facebook, and Apple '
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `us-72-x015` · US.92 · key-contradiction

**The key is D. Its explanation says: "D is wrong because the speech did not persuade France and Russia to support the invasion." — is the KEY still right, and if so what should this sentence say instead?**

> Secretary of State Colin Powell's February 2003 presentation to the UN Security Council on Iraqi WMDs is historically significant because —

*Checked:*
- key is 'D'; key text is "Powell later called it a 'blot' on his record after the WMD claims proved false"
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `us-73-x023` · US.66 · key-contradiction

**The key is A. Its explanation says: "A is wrong because Congress did not need to vote before FEMA could spend major disaster funds." — is the KEY still right, and if so what should this sentence say instead?**

> The Stafford Act governs FEMA's authority to respond to disasters. Katrina revealed its limitations because —

*Checked:*
- key is 'A'; key text is 'The Act required a congressional vote before FEMA could deploy resources exceedi'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `us-74-q02` · US.92 · key-contradiction

**The key is B. Its explanation says: "B is wrong because banks still had legal disclosure obligations, and C is wrong because the lesson was not that all financial innovation is inherently bad." — is the KEY still right, and if so what should this sentence say instead?**

> The 2008 financial crisis was rooted in a housing bubble inflated by risky mortgage lending. 'Subprime' mortgages were bundled into complex financial instruments (mortgage-backed securities) and sold to investors worldwide. When housing prices fell, these instruments became worthless. This crisis de…

*Checked:*
- key is 'B'; key text is 'Deregulation of the financial industry in the 1990s and 2000s had removed safegu'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `us-91-x028` · US.90 · key-contradiction

**The key is B. Its explanation says: "B is incorrect because it points to a different Cold War policy or country; D is incorrect because it points to a different Cold War policy or country." — is the KEY still right, and if so what should this sentence say instead?**

> China's admission to the World Trade Organization (2001) had long-term consequences including:

*Checked:*
- key is 'B'; key text is 'A massive transfer of American technology to China that accelerated its military'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
```

### `us-93-x015` · US.92 · key-contradiction

**The key is D. Its explanation says: "B is incorrect because it names a different institution or power than the one the item asks about; D is incorrect because it names a different institution or power than the one the item asks about." — is the KEY still right, and if so what should this sentence say instead?**

> The increasing diversity of the Supreme Court over the past 50 years reflects:

*Checked:*
- key is 'D'; key text is 'Changing political priorities of presidents who recognized the symbolic and prac'
- the sentence is a distractor rationale left pointing at the old key letter
- the RENDERED form is already correct — forms.remap_letters fixes the page

*Could NOT check:*
- whether the key itself is correct — that is a claim about history
- what the replacement sentence should assert

*Draft (not applied):*
```json
{
  "action": "delete the sentence and replace it with one saying why the key is right",
  "doNotDo": "deleting it outright leaves the rationale stopping mid-argument, which is the next defect"
}
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
