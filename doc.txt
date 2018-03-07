                    William's Crazy Word Generator
                             Version 2.0
                             July 27 2016

(Please see the file 'platform.txt' for Linux, MacOS, and Windows
setup instructions.)



This word generator is the work of about two years of on-and-off
attention.  It is focused on accomplishing certain tasks that I have
found impossible or very annoying in other word generator tools.

    * It is all Unicode all the time.  If you're running under X11,
      make sure your xterm has been told to use UTF-8.
    * If given a list of the graphemes (letters, digraphs or n-graphs)
      it will sort the resulting word list according to that scheme,
      regardless of how your local OS thinks Unicode collation should
      work.
    * It has basic phonological knowledge and can, with a switch, do
      voicing assimilation, coronal cluster metathesis, as you need
      it.
    * Phonemes are selected according to a natural distribution.  I
      use Gusein-Zade as good enough, and easier to parameterize than
      the Yule distribution.

This is a command line tool which is known to work under Linux and
OSX.  If someone wants to test it under Windows Python, please let me
know how it goes.


== Defining a Phonology ==

(See the file 'test.def' for an example phonology which has nearly
every feature on display.)

You can use '#' for comments in the file - everything after the sign
is ignored.

At the top of the definition file is the directive "with:" which is
used to select a few behaviors, all related to the assimilation
engine. The first option, 'std-ipa-features', loads up the feature
database with IPA values.  The other possibility here is
'std-digraph-features' which has my own demented non-IPA digraphs for
certain sounds (see the file 'SmartClusters.py' to see the n-graph
equivalents of IPA).  You probably want to stick with IPA if you use
this feature at all.

The next option is 'std-assimilations' which automatically performs
two kinds of assimilation on your generated words: nasal assimilation
(i.e., "np" > "mp") and voicing assimilation ("tg" > "dg").  Note that
with IPA features turned on, you can easily end up with the IPA symbol
for the velar nasal in your generated word list.  If you don't want
that, just use the filter line (explained below) to fix it.

The final option is 'coronal-metathesis' which fixes certain consonant
clusters.  In many languages, a cluster as in "atpo" is strongly
dispreferred.  I don't much care for it myself.  With the coronal
metathesis feature turned on, the above word is fixed to 'apto'.

The next directive is 'letters:'.  This must be defined if you want to
use any of the assimilation or metathesis features.  If you don't use
those, it isn't required, but if you *do* use it, it defines the sort
order of all wordlists.

*** Make sure there are no letters in your phoneme classes which don't
*** occur in the 'letters:' directive, or you'll get very strangly shaped
*** words!  Some day I'll write something to fix this.

The next section is the part you expect from a word generation tool:
single letters define phoneme classes which are used to define words.
The order in which they are given matches their frequency, according
to the Gusein-Zade distribution.  If you want to weight the phonemes
by hand, you must assign weights to all of them.  This is indicated
with a number attached to the phoneme with a colon, "a:7 i:2".

Next, in the "words:" directive you use the phoneme classed defined
above to create word shapes.  Again, the order for these determines
their frequency (a simple power law determined by eyeball).  If you
put a question mark after a class letter, the letter will only be
selected some of the time.  By default, the marked classes will only
occur about 10% of the time.  Use the 'random-rate:' directive to
change that to a different percent (0-100).  You can use letters
directly in the word definitions, so you could add glide clusters,
with CVC? and CyVC? and CwVC?.

If you allow a sequence of the same word class, but want to prevent
duplication, you can use the character '!'.  For example, given these
example phoneme classes:

    C = p t k h s m n l
    V = a i e u o

Let us imagine that vowels may occur in sequence, but they cannot be
the same vowel.  So, the word shape CVV! rule means "consonant, a
vowel, another vowel different from the previous one."  So, you will
get words like 'kia' and 'loe' but not 'hii'.

You cannot currently combine '?' and "!" options.

In general, it is better to define a bunch of word shapes without too
many options or letters, and just order them as makes the most sense
to you.

If you find yourself repeating certain patterns within words, you can
define macros to simplify your life.  Macros are defined like the
phoneme classes, except the macro starts with a dollar sign ($). It
must still be a single character long. Any pattern allowed in the
words directive can be in a macro.  For example:

    $S = CVD?
    words: CVCV? $S$S $S $S$S$S

In this $S defines a frequently repeated pattern. It could also be
used as part of a larger word definition, as in 'VD?$S', for example.

Macros *must* be defined before the 'words:' lines in which they are
used. 

Next are filters and rejections.  Both of these use regular
expressions to do their work.  For 'reject:' any pattern (no spaces
are allowed) occuring in a word will cause that word to be thrown
away.  You can have as many "reject:" lines as you like, or you can
put them all on a single line.

Filters ('filter:' directive) are indicated with

    "PATTERN-A > PATTERN-B"

where PATTERN-A is some collection of symbols you want to change, and
PATTERN-B is the replacement.  If you use regular expression groups in
the first part, you can use substitutions in the second:

    s(k|t) > \1s  (turns 'aska' into 'aksa')

If the pattern target (PATTERN-B) is an exclamation point, "!",
PATTERN-A is simply deleted. This could be useful, for example, if you
wanted to use a character to mark syllable boundaries, do some filters
based on that, then remove the syllable character as a final
filter. You will need to include the syllable boundary marker in the
'letters' directive, and it shouldn't be a period or any bracketing
character (parentheses, brackets, etc.).

You can have multiple 'filter:' lines, or several changes on a single
line, separated by a semicolon.

Finally, there are cluster tables. These combine filters and
rejections in a clear and concise way based on a layout sometimes seen
in descriptions of languages' phonologies.  For example:

    % a  i  u
    a +  +  o
    i -  +  uu
    u -  -  +

This table defines what do do about various vowel combinations. The
start of a cluster table *must* have a percent sign, '%', as the very
first character of the line. The phonemes following that represent the
*second* element in a cluster. The first phoneme in each following row
represent the *first* element in a cluster. Within the table, '+'
means the combination is fine, '-' means the combination should be
rejected, and anything else is a substitution. So 'a' + 'i' is fine,
but 'a' + 'u' becomes an 'o', while 'i' + 'a' is forbidden.

A blank line marks the end of a cluster table. These are just a
notational convenience, to lay out a bunch of rejects and
filters. Regular expressions can be used.  As with normal rejects and
filters, these are processed in order when a word is created. The
simple rejects and filters can come before or after a cluster table as
makes sense for what you're trying to accomplish.

See examples/hungarian.def for an extended example using the cluster
table option.

== Using the Command Line ==

The command 'lexifer' must take at least one argument, the name of the
phoneme definition file.  By default, it will spit out one
pseudo-paragraph of text, with punctuation, capitalization, etc., to
try to give you a feel for how the generator is working.

The option -n (or --number) instead prints out the number of words you
ask for,

    ./lexifer test.def -n 15

By default the word list is sorted if 'letters:' has been set.  If for
some reason you don't want that, -u (or --unsorted) will turn off that
behavior.

Finally, by default the output text is justified to 70 characters. If
instead you want one word per line, use -o (or --one-per-line).


--
William S. Annis
Madison, March 30 2015 (updated July 2016)
