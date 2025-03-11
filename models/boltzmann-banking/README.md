# The Boltzmann Banking System

## Overview

This program is an agent-based model built using Mesa. It simulates very basic economic activity using two types of agents: `Individual`s and `Bank`s. On each step, each `Individual` tries to give one unit of money to another `Individual`. If they can't because they do not have enough money, they can instead apply for a loan from a `Bank` as long as they are beneath their personal borrowing limit. The `Bank`s provide a means of payment between the `Individual`s, ie. a form of money, by offering them transaction accounts and allowing transfers between them.

For these models, loans will not bear any interest. Nor will there be any penalty for being unable to repay a loan, ie. defaulting. If an `Individual` defaults, they will simply keep trying to repay the loan in perpetuity. While an `Individual` is in default, they will be unable to give anyone else money.

---

## Future: Model with Simple Businesses

This is an agent-based model of a simple capitalist market economy that illustrates the most basic circular flow of a capitalist system: individuals buy goods and services from businesses that produce those goods and services by employing some individuals as workers and using their labor, and that are owned by other individuals who a dividend paid from the profits of their business.

In addition to this simple real economy, there is a financial system comprising many privately owned banks and a central bank that provides a payments system for individuals and businesses: each individual and business has an account at at one of the private banks and each private bank has an account at the central bank. That is, the money of our model economy is defined as the liabilities issued by the private banks, with the liabilities issued by the central bank acting as reserves for transfers between banks. Banks can borrow reserves from the central bank, and businesses can borrow money from the private banks.

There is also a government that sells bonds to the banks, spends money into the economy and can levy taxes.
