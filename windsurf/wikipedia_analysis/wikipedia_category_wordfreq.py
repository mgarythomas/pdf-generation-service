Event-driven architectures, on the other hand, are still based on asynchronous messaging and allow for lesser forms of coupling between components.

Poll based Events
- Easier to control throughput and concurrency
- Fault tolerance in processing easier to achieve

Commands
Commands are used to represent requests for actions that change state in the system. A command is an instruction and is normally directed to an intended recipient.

Event Sourcing
A state model is used to represent the current state of the system by replaying the sequence of events.

Commands and Events
In systems designed with Domain-Driven Design (DDD), commands and events typically correspond to actions and outcomes within specific bounded contexts.

CQRS
This pattern is often used in conjunction with event sourcing and DDD, to better capture intent and optimise performance.

### Bounded Context Scenario

To further illustrate the concepts of commands, events, and bounded contexts in a Domain-Driven Design (DDD) environment, consider the example of an online retail platform. The system is composed of several bounded contexts, each owning its domain logic and data.

#### Bounded Contexts

- **Order Management**
- **Inventory Management**
- **Payment**
- **Shipping**

Each context communicates asynchronously using domain events, ensuring loose coupling and autonomy.

#### Example Flow: Customer Places an Order

**1. Order Management**
- Command: `PlaceOrder` — triggered by a customer via the web interface.
- The context persists the order with a “Pending” status.
- Event Emitted: `OrderPlaced`.

**2. Inventory Management**
- Listens for the `OrderPlaced` event.
- Checks inventory and issues the `ReserveStock` command.
- Emits: `StockReserved` or `StockNotAvailable`.

**3. Payment**
- Listens for `StockReserved`.
- Processes payment via the `ProcessPayment` command.
- Emits: `PaymentConfirmed` or `PaymentFailed`.

**4. Shipping**
- Listens for `PaymentConfirmed`.
- Initiates shipment via the `CreateShipment` command.
- Emits: `ShipmentCreated`.

#### Summary of Concepts

| Concept               | Role in Scenario                                         |
|----------------------|----------------------------------------------------------|
| **Command**           | Represents intent (e.g., `PlaceOrder`, `ProcessPayment`) |
| **Event**             | Represents outcome (e.g., `OrderPlaced`, `StockReserved`) |
| **Bounded Context**   | Encapsulates domain-specific logic and data              |
| **Loose Coupling**    | Communication via asynchronous events                    |
| **Scalability & Fault Tolerance** | Contexts operate and scale independently              |
