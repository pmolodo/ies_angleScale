...or, more precisely, since the above is undefined at $angleScale = -1$:

$$
\theta_{ies} =
\begin{dcases}
    \frac{\theta_{light} - \pi}{1 + angleScale} + \pi,
        & \text{if} \quad angleScale > -1               \\
    0,  & \text{if} \quad angleScale \leq -1            \\
\end{dcases}
$$
