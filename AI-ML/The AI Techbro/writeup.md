# Challenge


 The AI Techbro — Neural Password Bypass


##Approach

**Category:** AI / Machine Learning  


This challenge replaces traditional password hashing with a neural encoder.  
Instead of verifying a hash, the system embeds a 16-character string into a 4-dimensional vector and checks whether that vector is sufficiently close to a predefined target.


Our objective was not to recover *the* password, but to find *any* input that produces an embedding within the allowed tolerance.


Because neural networks are not collision-resistant, this turns into an optimization problem rather than a cryptographic one.


---


## Methodology


The following artifacts were provided:


- `checker.py`  
  Contains the full PyTorch model definition. The network consists of multiple dense layers, two block-sparse layers, and a gated activation stage.


- `encoder_weights_updated.npz`  
  Serialized weights for the pretrained encoder.


### Constants


- Input length: **16 characters**
- Alphabet: lowercase letters + digits (`a–z`, `0–9`)
- Target vector:



[-8.175837, -1.710289, -0.7002581, 5.3449903]



- Acceptance threshold:



0.00025



---


## Understanding the Encoder


Each candidate string is processed as follows:


1. Characters are converted to ASCII.
2. Values are normalized:



(ascii - 80) / 40



3. The resulting 16-dimensional vector is passed through the neural network.
4. The model outputs a 4-dimensional embedding.
5. Validation succeeds if:



|| embedding − target || < threshold



This architecture performs a drastic dimensionality reduction:



16 dimensions → 4 dimensions



That alone guarantees collisions.


Unlike cryptographic hashes, this mapping is:


- Continuous
- Deterministic
- Many-to-one


Which means a huge number of inputs can satisfy the same constraint.


The theoretical search space is:



36^16 ≈ 8 × 10^24



Clearly impossible to brute force directly.


---


## Core Idea


Since the model is known and callable locally, the problem becomes:


> Find a 16-character string minimizing the Euclidean distance to the target vector.


This is essentially black-box optimization over discrete variables.


Gradients are useless due to character constraints, so I used stochastic and greedy heuristics.


---


## Methodology


### Phase 1 — Local Improvement


Starting from random strings:


- Iterate over each character position.
- Try all 36 symbols at that index.
- Keep the choice that reduces distance the most.
- Repeat until no further improvement occurs.


This behaves like coordinate descent.  
It converges fast, but frequently lands in shallow local minima.


---


### Phase 2 — Probabilistic Escapes


To avoid stagnation, simulated annealing is introduced:


- Randomly modify 1–3 characters.
- Evaluate the new candidate.
- Accept worse results with probability:



exp(-Δ / T)



- Temperature decays exponentially over time.


Early iterations explore broadly.  
Later iterations focus on fine tuning.


---


### Phase 3 — Hybrid Loop


The solver alternates between:


1. Greedy refinement
2. Annealing-based exploration
3. Final greedy cleanup


Multiple random restarts are used to improve reliability.


Batch inference is leveraged to speed up evaluation.


---


## Implementation Highlights


Contained in `solver.py`:


- Vectorized scoring for candidate strings
- Exponential cooling schedule
- Random restarts
- Character-wise greedy optimization
- Annealing mutations of variable size


This combination consistently converges to a valid solution in under a few minutes on CPU.


---


## Outcome


Recovered candidate:



bucwheqy16423870   # Note - Its a neural network , It doesnot have a unique password, Every time you run the script, the password changes. 



Encoder output:



[-8.175898, -1.7102152, -0.70017946, 5.3450875]



Target:



[-8.175837, -1.710289, -0.7002581, 5.3449903]



Final distance:



0.000157 (< 0.00025 threshold)



The checker accepts this input.


---


## Flag



root{50_57up!d_it5_br!ll!@n7}
