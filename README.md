# CRANK

## A laboratory for studying what consequences can change.

You have a small system.

It can do a few things.

Something happened.

The system was wrong.

You may change **one thing**.

What do you change?

[**Start the first experiment →**](#the-first-experiment)

---

## 1. The world

The laboratory gives the system a small world to operate in.

There are inputs.

There are outputs.

There are consequences.

The system tries something.

The world tells us what happened.

That's it.

For now, you do not need to know how the system is built.

You only need to operate it.

---

## 2. Something goes wrong

The system receives:

```text
[2, 0, 1]
```

It produces:

```text
[2, 0, 1]
```

The evaluator says the correct result was:

```text
[2, 1, 0]
```

The system was wrong.

You now have a choice.

---

## 3. You get one change

You may change **exactly one thing**.

You could make the system remember this case.

You could change how it performs the task.

You could give it a new construction primitive.

You could change the rule that decides what kind of change to make.

But you only get one.

Before choosing, ask:

> **What actually needs to change for the system to succeed?**

Don't worry about the notation yet.

Just make the best change you can.

---

## 4. Try it

Run the experiment.

Then run it again on a fresh case.

Watch what changes.

A successful first attempt does not necessarily mean you found the right mechanism.

A system can remember an answer without learning a procedure.

It can have the right procedure without knowing when to use it.

It can have the right tools without being able to construct the needed operation.

And it can successfully solve a problem while continuing to make the same mistake about **what should be changed next**.

The laboratory is designed to separate these cases.

---

## 5. See what happened

Run the experiment and inspect which component changed.

If the successful intervention changed what the system retains between experiences, then:

```math
\boxed{\text{you just changed }M}
```

Here, `M` means the system's persistent learned state.

That distinction matters because changing memory is only **one kind of learning**.

The campaign will ask what happens when memory is not enough.

---

# Level 1 — Can you change what it remembers?

You will encounter a problem that can be solved by changing persistent state while leaving the rest of the system alone.

Your task:

> **Find the smallest change that works.**

Then test it on fresh cases.

The laboratory will tell you whether the change generalized or merely memorized the encounter.

### Laboratory question

```math
\boxed{\text{Can consequence change what the system remembers?}}
```

---

## Why this matters

CRANK studies a simple question with increasingly difficult consequences:

> **What is experience actually allowed to change?**

At first, the answer might be:

```text
memory
```

Then perhaps:

```text
procedure
```

Then:

```text
construction space
```

And eventually:

```text
the rule that determines where future changes should happen
```

We will introduce names for these only when the experiments make the distinctions necessary.

---

## The trust rules

**The guide tells you what to ask.**  
**The laboratory tells you what happened.**

And:

**Every result has a path from the lesson to the raw artifact that produced it.**

A lesson is not a result.

A diagram is not a result.

A claim is not a result.

The experiment, its records, and its machine-checkable artifacts determine what can actually be concluded.

---

## Where to go next

Start with the first experiment.

Then follow the problem wherever it leads.

The deeper formal definitions, experimental contracts, certificates, and raw records are there when you need them—not before.

```math
\boxed{\text{learn}\rightarrow\text{try}\rightarrow\text{break}\rightarrow\text{measure}\rightarrow\text{verify}}
```
