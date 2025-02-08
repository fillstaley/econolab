# The Boltzmann Banking System

## Overview

This program is an agent-based model built using Mesa. The model simulates very basic economic activity using two types of agents: `Individual`s and `Bank`s.

---

## Old overview

This model involves many individuals and a single bank. The individuals simply try
to give each other one unit of money. If they do not have enough money, they may
apply for a loan from the bank. If the bank approves the loan, they will grant the
individual money in the form of a bank account.

The bank loans that will be offered will not bear any interest. When they come due,
individuals will try to repay them before trying to give money to someone else. If
they are unable to repay the loan, ie. if they default, then they will be unable to
give anyone else money. The individual will then try again on the next step. Once
they successfully repay the loan, they will then be ineligible to borrow any money
for some number of steps.

---

## Future: Model with Simple Businesses

This is an agent-based model of a simple capitalist market economy that illustrates the most basic circular flow of a capitalist system: individuals buy goods and services from businesses that produce those goods and services by employing some individuals as workers and using their labor, and that are owned by other individuals who a dividend paid from the profits of their business.

In addition to this simple real economy, there is a financial system comprising many privately owned banks and a central bank that provides a payments system for individuals and businesses: each individual and business has an account at at one of the private banks and each private bank has an account at the central bank. That is, the money of our model economy is defined as the liabilities issued by the private banks, with the liabilities issued by the central bank acting as reserves for transfers between banks. Banks can borrow reserves from the central bank, and businesses can borrow money from the private banks.

There is also a government that sells bonds to the banks, spends money into the economy and can levy taxes.
